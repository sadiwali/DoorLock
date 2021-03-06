package terafloat.circlebot.Activities;

import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.Intent;
import android.graphics.PorterDuff;
import android.os.Handler;
import android.os.Message;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import java.util.Arrays;

import terafloat.circlebot.BluetoothComms.BluetoothConnection;
import terafloat.circlebot.Constants.Const;
import terafloat.circlebot.Exceptions.NoConnectionException;
import terafloat.circlebot.R;

public class MainActivity extends Activity {
    // tag for debugger
    private static final String TAG = "MainActivity";

    // interaction
    private Button btnConnect;
    private Button btnDisconnect;
    private Button btnSendHello;
    private Button btnMore;
    private Button btnLock;
    private Button btnUnlock;
    private TextView lblStatus;

    private boolean isLocked = true;

    // variables

    //private BluetoothAdapter mBluetoothAdapter; // bluetooth adapter
    // stores devices paired and found

    private Handler mHandler = new Handler(){
        @Override
        public void handleMessage(Message msg) {
            // TODO Auto-generated method stub
            Log.i(TAG, "in handler");
            super.handleMessage(msg);
            switch(msg.what){

                case BluetoothConnection.MESSAGE_READ:
                    byte[] readBuf = (byte[])msg.obj;
                    // create a copy of the buffer with length equal to the number of letters
                    byte[] fixedLenBuf = Arrays.copyOfRange(readBuf, 0, msg.arg1);
                    // convert to string
                    String string = new String(fixedLenBuf);
                    // received a string message, process it
                    processMessage(string);
                    break;
                case BluetoothConnection.MESSAGE_SENT:
                    readBuf = (byte[])msg.obj;
                    // create a copy of the buffer with length equal to the number of letters
                    fixedLenBuf = Arrays.copyOfRange(readBuf, 0, msg.arg1);
                    // convert to string
                    string = new String(fixedLenBuf);
                    Log.i(TAG, "Sent message: " + string);
                    Toast.makeText(getApplicationContext(), string, Toast.LENGTH_SHORT).show();
                    break;
                case BluetoothConnection.CONNECTION_STARTED:
                    Log.i(TAG, "Connection started...");
                    changeModeConnected();
                    break;
                case BluetoothConnection.CONNECTION_DISCONNECT:
                    Log.i(TAG, "Connection ended...");
                    changeModeDisconnected();
                    break;
                case BluetoothConnection.COULD_NOT_CONNECT:
                    // did not start the connected thread
                    Log.i(TAG, "Connection could not be established...");
                    lblStatus.setText("Could not connect.");
                    break;

            }
        }
    };

    private void changeModeDisconnected() {
        lblStatus.setText("Disconnected.");
        btnUnlock.setText("DISCONNECTED");
        btnUnlock.getBackground().setColorFilter(getResources()
                .getColor(R.color.colorDisabled), PorterDuff.Mode.SRC_ATOP);
    }

    private void changeModeConnected() {
        lblStatus.setText("Connected.");
        btnUnlock.setText("UNLOCK");
        btnUnlock.getBackground().setColorFilter(getResources()
                .getColor(R.color.colorPrimaryDark), PorterDuff.Mode.SRC_ATOP);
    }


    @Override
    public void onPause() {
        super.onPause();
    }

    @Override
    public void onResume() {
        super.onResume();
        // re-install handler for current activity
        BluetoothConnection.getInstance().installHandler(mHandler);
        updateScreens();
    }

    /**
     * Process a string received from the RPI
     * @param message is the string message received.
     */
    private void processMessage(String message) {
        Log.i(TAG, "Received message: " + message);
        Toast.makeText(getApplicationContext(), message, Toast.LENGTH_SHORT).show();


        if (message.equalsIgnoreCase(Const.ST_LOCKED)) {
            // door was locked,
            isLocked = true;
            btnUnlock.setText("UNLOCK");
            // color will be blue for safe
            btnUnlock.getBackground().setColorFilter(getResources()
                    .getColor(R.color.colorPrimaryDark), PorterDuff.Mode.SRC_ATOP);


        } else if (message.equalsIgnoreCase(Const.ST_UNLOCKED)) {
            // door was just unlocked
            isLocked = false;
            btnUnlock.setText("LOCK");
            // color will be red for danger
            btnUnlock.getBackground().setColorFilter(getResources()
                    .getColor(R.color.colorAccent), PorterDuff.Mode.SRC_ATOP);
        } else {
            Log.d(TAG, "Received process message: " + message);
        }
    }

    /**
     * Update the displays in activity.
     */
    private void updateScreens() {
        if (BluetoothConnection.getInstance().isConnected()) {
            lblStatus.setText("Connected.");
        } else {
            lblStatus.setText("Disconnected.");
        }
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.i(TAG, "onCreate");
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.activity_main);
        init(); // initialize the program

        if(!BluetoothConnection.getInstance().isCapable()) {
            Toast.makeText(getApplicationContext(), "Device not BT capable", Toast.LENGTH_SHORT).show();
            finish();
        }
        // attempt to enable bluetooth
        if (!BluetoothConnection.getInstance().isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivity(enableBtIntent); // ask the user for bluetooth enabling
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        //
        super.onActivityResult(requestCode, resultCode, data);
        if(resultCode == RESULT_CANCELED){
            Toast.makeText(getApplicationContext(), "Bluetooth must be enabled to continue", Toast.LENGTH_SHORT).show();
            finish();
        }
    }

    /**
     * Initialize the program.
     */
    private void init() {

        // set up interaction
        this.btnConnect = findViewById(R.id.btnConnect);
        this.btnConnect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                connectToDevice(BluetoothConnection.getInstance().getDeviceWithName("raspberrypi"));
            }
        });

        this.btnDisconnect = findViewById(R.id.btnDisconnect);
        this.btnDisconnect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.i(TAG, "Disconnect button click");
                BluetoothConnection.getInstance().disconnect();
            }
        });

        this.btnMore = findViewById(R.id.btnMore);
        this.btnMore.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent moreIntent = new Intent(getApplicationContext(), MoreActivity.class);
                startActivity(moreIntent);
            }
        });

        this.lblStatus = findViewById(R.id.lblConnectStatus);


        this.btnUnlock = findViewById(R.id.btnUnlock);
        btnUnlock.setText("DISCONNECTED");
        changeModeDisconnected();
        this.btnUnlock.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                   lockUnlockFcn();
                } catch (NoConnectionException e) {
                    Log.i(TAG, "Message not sent because device disconnected.");
                }
            }
        });
    }

    /**
     * Toggle for the lock and unlock button
     * @throws NoConnectionException
     */
    private void lockUnlockFcn() throws NoConnectionException {

        if (isLocked) {
            // locked, so unlock
            BluetoothConnection.getInstance().sendMessage("DO_UNLOCK");
        } else {
            // unlocked, so lock
            BluetoothConnection.getInstance().sendMessage("DO_LOCK");
        }
    }

    /**
     * Connect to the main device, only done in MainActivity.
     */
    private void connectToDevice(BluetoothDevice deviceToConnectTo) {
        // set up the initial connection with my handler
        lblStatus.setText("Connecting...");
        BluetoothConnection.getInstance().setupConnection(mHandler, deviceToConnectTo);
    }

}
