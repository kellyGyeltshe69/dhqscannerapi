# # repository/qr_generator.py
# import qrcode


# def generate_qr_code(user_id, date):
#     # data = f"User: {user_id}, Date: {date}"
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     ) 
#     qr.make(fit=True)

#     img = qr.make_image(fill_color="black", back_color="white")
#     img.save(f"qrcodes/{user_id}_{date}.png")  # Save QR code to a file or database
 