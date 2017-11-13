import time
def dbug(PARCEL: '[bool, str]', msg: 'obj') -> None:
    ''' Print a debug message, given a parcel with the 
    debug status, and tag to print, along with the message
    or object to print. 

    REQ: len(PARCEL) == 2
         PARCEL contains the debug condition and TAG

    '''
    DEBUG = PARCEL[0] # to enable/disable debugging
    TAG = PARCEL[1] # the TAG of the class printing the debug statements
    if (DEBUG):
        print("dbug [" + str(time.time()) + "s]: "  + TAG + ": " + str(msg))