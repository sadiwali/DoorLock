package terafloat.circlebot.Activities;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.Intent;
import android.os.Handler;
import android.os.Message;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import java.util.Arrays;

import terafloat.circlebot.BluetoothComms.BluetoothConnection;
import terafloat.circlebot.Constants.Const;
import terafloat.circlebot.Exceptions.NoConnectionException;
import terafloat.circlebot.R;

public class MainActivity extends AppCompatActivity {
    // tag for debugger
    private static final String TAG = "MainActivity";

    // interaction
    private Button btnConnect;
    private Button btnDisconnect;
    private Button btnSendHello;
    private Button btnMore;
    private TextView lblStatus;

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
                    Log.i(TAG, "Received message: " + string);
                    Toast.makeText(getApplicationContext(), string, Toast.LENGTH_SHORT).show();
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
                    lblStatus.setText("Connected.");
                    break;
                case BluetoothConnection.CONNECTION_DISCONNECT:
                    Log.i(TAG, "Connection ended...");
                    lblStatus.setText("Disconnected.");
                    break;
                case BluetoothConnection.COULD_NOT_CONNECT:
                    // did not start the connected thread
                    Log.i(TAG, "Connection could not be established...");
                    lblStatus.setText("Could not connect.");
                    break;

            }
        }
    };


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
        this.btnConnect = (Button) findViewById(R.id.btnConnect);
        this.btnConnect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                connectToDevice(BluetoothConnection.getInstance().getDeviceWithName("raspberrypi"));
            }
        });

        this.btnDisconnect = (Button) findViewById(R.id.btnDisconnect);
        this.btnDisconnect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.i(TAG, "Disconnect button click");
                BluetoothConnection.getInstance().disconnect();
            }
        });

        this.btnSendHello = (Button) findViewById(R.id.btnSendData);
        this.btnSendHello.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    BluetoothConnection.getInstance().sendMessage("hello cats");
                } catch (NoConnectionException e) {
                    Log.i(TAG, "Message not sent because device disconnected.");
                }
            }
        });

        this.btnMore = (Button) findViewById(R.id.btnMore);
        this.btnMore.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent moreIntent = new Intent(getApplicationContext(), MoreActivity.class);
                startActivity(moreIntent);
            }
        });

        this.lblStatus = (TextView) findViewById(R.id.lblConnectStatus);

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
