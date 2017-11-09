package terafloat.circlebot.Activities;

import android.os.Handler;
import android.os.Message;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import java.util.Arrays;

import terafloat.circlebot.BluetoothComms.BluetoothConnection;
import terafloat.circlebot.Constants.Const;
import terafloat.circlebot.Exceptions.NoConnectionException;
import terafloat.circlebot.R;

public class MoreActivity extends AppCompatActivity {
    private static final String TAG = "MoreActivity";
    private Button btnSendData;

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
                case BluetoothConnection.CONNECTION_DISCONNECT:
                    Toast.makeText(getApplicationContext(), "The connection was ended.", Toast.LENGTH_SHORT).show();
                    finish();

            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_more);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);

        BluetoothConnection.getInstance().installHandler(mHandler);


        init();
    }

    private void init() {

        this.btnSendData = (Button) findViewById(R.id.btnSend);
        this.btnSendData.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    BluetoothConnection.getInstance().sendMessage("Hello cats!!!");
                } catch (NoConnectionException e) {
                    Log.i(TAG, "MESSAGE NOT SENT");
                }
            }
        });


    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case android.R.id.home:
                // app icon in action bar clicked; goto parent activity.
                this.finish();
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }


}
