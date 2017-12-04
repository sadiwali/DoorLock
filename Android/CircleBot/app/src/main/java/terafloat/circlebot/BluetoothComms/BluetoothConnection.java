package terafloat.circlebot.BluetoothComms;

import android.app.Application;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Handler;
import android.os.Message;
import android.text.LoginFilter;
import android.util.Log;
import android.widget.Toast;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import terafloat.circlebot.Constants.Const;
import terafloat.circlebot.Exceptions.NoConnectionException;

/**
 * Created by sadiw on 2017-10-11.
 */

public class BluetoothConnection extends Application {
    private static final String TAG = "BluetoothConnection";
    // Constants relating to bluetooth connection
    // add constants here for handler functions
    public static final int MESSAGE_READ = 1;
    public static final int MESSAGE_SENT = 2;
    public static final int CONNECTION_DISCONNECT = 3;
    public static final int CONNECTION_STARTED = 4;
    public static final int COULD_NOT_CONNECT = 5;

    private boolean paused = false;

    // main instance object
    private static BluetoothConnection mInstance;

    // list storing Bluetooth devices
    private ArrayList<BluetoothDevice> pairedDevices;
    private ArrayList<BluetoothDevice> foundDevices;

    private ConnectedThread mConnectedThread; // the connected thread
    private static final UUID MY_UUID = UUID.fromString("94f39d29-7d6d-437d-973b-fba39e49d4ee");
    private BluetoothAdapter mBluetoothAdapter; // system's bt adapter


    /**
     * Initialize the BluetoothConnection class.
     */
    public void onCreate() {
        super.onCreate();
        mInstance = this;

        this.registerBroadCastReceiver();

        // get the bluetooth adapter
        this.mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        this.foundDevices = new ArrayList<>();
        this.pairedDevices = new ArrayList<>();
        populatePairedDevices(); // populate list of paired devices for connecting
    }

    private void registerBroadCastReceiver() {
        // listen for actions
        IntentFilter filter = new IntentFilter();
        filter.addAction(BluetoothDevice.ACTION_ACL_CONNECTED);
        filter.addAction(BluetoothDevice.ACTION_ACL_DISCONNECT_REQUESTED);
        filter.addAction(BluetoothDevice.ACTION_ACL_DISCONNECTED);
        filter.addAction(BluetoothDevice.ACTION_FOUND);
        filter.addAction(BluetoothAdapter.ACTION_DISCOVERY_STARTED);
        filter.addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED);
        filter.addAction(BluetoothAdapter.ACTION_STATE_CHANGED);

        registerReceiver(mReceiver, filter);
    }


    /**
     * Check if device is bluetooth capable.
     * @return true if capable, false otherwise.
     */
    public boolean isCapable() {
        if (this.mBluetoothAdapter == null) {
            return false;
        } else {
            return true;
        }
    }

    /**
     * Check if device enabled.
     * @return true if enabled, false otherwise.
     */
    public boolean isEnabled() {
        if (isCapable()) {
            return this.mBluetoothAdapter.isEnabled();
        } else {
            return false;
        }
    }

    /**
     * Get the bluetooth connection instance.
     * @return the instance of bluetooth connection.
     */
    public static BluetoothConnection getInstance() {
        return mInstance;
    }

    /**
     * Check if bluetooth is connected to the main device.
     * @return true if connected, false otherwise.
     */
    public boolean isConnected() {
        if (this.mConnectedThread == null) {
            return false;
        } else {
            if (this.mConnectedThread.getState().equals(Thread.State.TERMINATED)) {
                return false;
            } else {
                return true;
            }
        }
    }

    /**
     * Send a string message through bluetooth.
     * @param message is the message to send.
     */
    public void sendMessage(String message) throws NoConnectionException {
        if (isConnected()) {
            this.mConnectedThread.sendMessage(message);
        } else {
            throw new NoConnectionException("Not connected to device.");
        }
    }

    public boolean isLocked() {
        return false;
    }

    // Create a BroadcastReceiver for actions
    private final BroadcastReceiver mReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (action.equals(BluetoothDevice.ACTION_FOUND)) {
                // Discovery has found a device. Get the BluetoothDevice
                // object and its info from the Intent.
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                foundDevices.add(device);
                Toast.makeText(getApplicationContext(), "Found device", Toast.LENGTH_SHORT).show();
                Log.i(TAG, device.getName() + " found on discovery.");
            } else if (action.equals(BluetoothAdapter.ACTION_DISCOVERY_STARTED)) {
                Log.i(TAG, "started discovery");
                Toast.makeText(getApplicationContext(), "Discovering...", Toast.LENGTH_SHORT).show();
            } else if (action.equals(BluetoothAdapter.ACTION_DISCOVERY_FINISHED)) {
                Log.i(TAG, "finished discovery");

            } else if (action.equals(BluetoothDevice.ACTION_ACL_CONNECTED)) {
                Log.i(TAG, "ACL connected");

            } else if (action.equals(BluetoothDevice.ACTION_ACL_DISCONNECT_REQUESTED)) {
                Log.i(TAG, "ACL disconnec requested");
            } else if (action.equals(BluetoothDevice.ACTION_ACL_DISCONNECTED)) {
                Log.i(TAG, "ACL disconnected");
            } else if (action.equals(BluetoothAdapter.ACTION_STATE_CHANGED)) {
                final int state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE,
                        BluetoothAdapter.ERROR);

                switch (state) {
                    case BluetoothAdapter.STATE_OFF:
                        Log.e(TAG, "Bluetooth off...");
                        break;
                    case BluetoothAdapter.STATE_TURNING_OFF:
                        disconnect();
                        Log.e(TAG, "Bluetooth turning off...");
                        // maybe use another handler for BluetoothConnection events
                        break;
                    case BluetoothAdapter.STATE_ON:
                        Log.e(TAG, "Bluetooth on...");
                        break;
                    case BluetoothAdapter.STATE_TURNING_ON:
                        Log.e(TAG, "Bluetooth turning on...");
                        break;
                }
            } else {
                Log.i(TAG, "some other action");
            }
        }
    };

    /**
     * A thread which connects to the bluetooth device passed.
     */
    private class ConnectThread extends Thread {
        private final BluetoothSocket mmSocket;
        private final BluetoothDevice mmDevice;
        private Handler mHandler;

        public ConnectThread(BluetoothDevice device, Handler handler) {
            // Use a temporary object that is later assigned to mmSocket
            // because mmSocket is final.
            BluetoothSocket tmp = null;
            mmDevice = device;
            this.mHandler = handler;

            try {
                // Get a BluetoothSocket to connect with the given BluetoothDevice.
                // MY_UUID is the app's UUID string, also used in the server code.
                tmp = device.createRfcommSocketToServiceRecord(MY_UUID);
            } catch (IOException e) {
                Log.e(TAG, "Socket's create() method failed", e);
            }
            mmSocket = tmp;
        }

        public void run() {
            // Cancel discovery because it otherwise slows down the connection.
            mBluetoothAdapter.cancelDiscovery();

            try {
                // Connect to the remote device through the socket. This call blocks
                // until it succeeds or throws an exception.
                mmSocket.connect();
            } catch (IOException connectException) {
                // Unable to connect; close the socket and return.
                Log.i(TAG, "could not connect");
                mHandler.obtainMessage(COULD_NOT_CONNECT).sendToTarget();
                try {
                    mmSocket.close();
                } catch (IOException closeException) {
                    Log.e(TAG, "Could not close the client socket", closeException);
                }
                return;
            }

            // The connection attempt succeeded. Perform work associated with
            // the connection in a separate thread.
            manageMyConnectedSocket(mmSocket, mHandler);
        }
    }

    /**
     * A connected socket is ready for data transfer. Create and manage a ConnectedThread.
     * @param mmSocket the bluetooth socket which is ready for data transfer.
     */
    private void manageMyConnectedSocket(BluetoothSocket mmSocket, Handler mHandler) {
        this.mConnectedThread = new ConnectedThread(mmSocket,mHandler);
        this.mConnectedThread.start();
    }

    /**
     * Thread which manages an open connection
     */
    public class ConnectedThread extends Thread implements Serializable {
        private static final String TAG = "ConnectedThread";

        private final BluetoothSocket mmSocket;
        private final InputStream mmInStream;
        private final OutputStream mmOutStream;
        private byte[] mmBuffer; // mmBuffer store for the stream

        private Handler mHandler; // handler to send data back to

        /**
         * Initialize the connected thread with the socket, and the handler.
         *
         * @param socket   is the open bluetooth socket passed in from ConnectThread.
         * @param mHandler is the handler to send data back to.
         */
        public ConnectedThread(BluetoothSocket socket, Handler mHandler) {
            this.mHandler = mHandler;
            this.mmSocket = socket;

            InputStream tmpIn = null;
            OutputStream tmpOut = null;

            // Get the input and output streams; using temp objects because
            // member streams are final.
            try {
                tmpIn = socket.getInputStream();
            } catch (IOException e) {
                Log.e(TAG, "Error occurred when creating input stream", e);
            }
            try {
                tmpOut = socket.getOutputStream();
            } catch (IOException e) {
                Log.e(TAG, "Error occurred when creating output stream", e);
            }

            mmInStream = tmpIn;
            mmOutStream = tmpOut;
            mHandler.obtainMessage(CONNECTION_STARTED).sendToTarget();
        }

        // the running function of the thread keeps listening for incoming data
        public void run() {
            mmBuffer = new byte[1024];
            int numBytes; // bytes returned from read()

            // Keep listening to the InputStream until an exception occurs.
            while (true) {
                try {
                    // Read from the InputStream.
                    numBytes = mmInStream.read(mmBuffer);

                    if (numBytes == -1) {
                        Log.i(TAG, "returned -1");
                    }

                    // Send the obtained bytes to the UI activity.
                    mHandler.obtainMessage(MESSAGE_READ, numBytes, -1, mmBuffer)
                            .sendToTarget();
                } catch (IOException e) {
                    Log.d(TAG, "Input stream was disconnected", e);
                    cancel();
                    break; // close the thread
                }
            }
        }

        // write bytes to bluetooth
        public void write(byte[] bytes) {
            try {
                mmOutStream.write(bytes);
                // Share the sent message with the UI activity.
                mHandler.obtainMessage(MESSAGE_SENT, bytes.length, -1, bytes)
                        .sendToTarget();
            } catch (IOException e) {
                Log.e(TAG, "Error occurred when sending data", e);
            }
        }

        /**
         * Change the handler for another activity.
         *
         * @param handler is the handler to set to.
         */
        public void changeHandler(Handler handler) {
            this.mHandler = handler;
        }

        /**
         * Send a string message through bluetooth.
         *
         * @param message is the message to send.
         */
        public void sendMessage(String message) {
            // convert message to bytes, then send
            write(message.getBytes());
        }

        // Call this method to shut down the connection.
        public void cancel() {
            try {
                mmSocket.close();
                // let the handler know
                mHandler.obtainMessage(CONNECTION_DISCONNECT).sendToTarget();
            } catch (IOException e) {
                Log.e(TAG, "Could not close the connect socket", e);
            }
        }
    }

    /**
     * Used to install the current activity's handler to the current connection to
     * receive data when it arrives.
     * @param handler is the handler of the activity.
     */
    public void installHandler(Handler handler) {
       if (isConnected()) {
            this.mConnectedThread.changeHandler(handler);
        }
    }

    /**
     * Set up a connection (Start a connection)
     * @param mHandler is the handler from the activity.
     * @param deviceToConnectTo is the given device to connect to.
     */
    public void setupConnection(Handler mHandler, BluetoothDevice deviceToConnectTo) {
        if (isConnected()) {
            // return if already connected
            return;
        }
        // enable bluetooth
        if (!mBluetoothAdapter.isEnabled()) {
           return;
        }

        Log.i(TAG, "Attempting to set up connection with " + deviceToConnectTo.getName());

        if (this.pairedDevices.contains(deviceToConnectTo)) {
            ConnectThread cThread = new ConnectThread(deviceToConnectTo, mHandler);
            cThread.start();

        } else {
            Log.e(TAG, "Device not paired. Will not connect.");
        }
    }

    /**
     * Get list of paired devices.
     * @return list of BluetoothDevice.
     */
    public List<BluetoothDevice> getPairedDevices() {
        return this.pairedDevices;
    }

    /**
     * Get list of found devices.
     * @return list of BluetoothDevice.
     */
    public List<BluetoothDevice> getFoundDevices() {
        return this.foundDevices;
    }

    /**
     * Get a bluetooth device given its name.
     * If the device is not paired, return null.
     * @param deviceName name of device to return.
     * @return the device if it is paired, or null if not.
     */
    public BluetoothDevice getDeviceWithName(String deviceName) {
        for (BluetoothDevice bD : this.pairedDevices) {
            if (bD.getName().equals(deviceName)) {
                return bD;
            }
        }
        return null;
    }

    /**
     * Disconnect the bluetooth connection, if connected.
     */
    public void disconnect() {
        if (isConnected()) {
            Log.i(TAG, "disconnect requested.");
            this.mConnectedThread.cancel();

        }
    }


    /**
     * Populate the list of paired devices.
     */
    private void populatePairedDevices() {
        if (!isCapable()) {
            return;
        }
        // get devices paired only if BT is capable.
        Set<BluetoothDevice> devicesArray;
        devicesArray = mBluetoothAdapter.getBondedDevices();

        Log.i(TAG, String.valueOf(devicesArray.size()));

        if(devicesArray.size()>0){
            for(BluetoothDevice device:devicesArray){
                // add only if unique
                if (!this.pairedDevices.contains(device)) {
                    this.pairedDevices.add(device);
                    Log.i(TAG, device.getName() + " added.");
                }

            }
        }
    }
}
