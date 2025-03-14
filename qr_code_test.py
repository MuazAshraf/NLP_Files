import qrcode

# Data to be encoded
data = "https://ashrafs.com.co"

# Create a QR code object
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# Add data to the QR code object
qr.add_data(data)
qr.make(fit=True)

# Create an image from the QR code object
img = qr.make_image(fill='black', back_color='white')

# Save the image to a file
img.save('qrcode.png')
