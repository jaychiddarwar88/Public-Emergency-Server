import hashlib

def encryptstring(strconv):
	shasign = (hashlib.sha256(strconv.encode())).hexdigest()

	return shasign
