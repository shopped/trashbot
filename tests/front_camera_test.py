import tflite
# this will only work in root directory

messenger = tflite.Messenger()
print(messenger.get_message())
print(messenger.get_message())
print(messenger.get_message())
messenger.close()
