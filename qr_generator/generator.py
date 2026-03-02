import qrcode
import os

def create_student_qr(surs_mail: str, output_folder: str = "output"):
    """
    Generates a QR code for a given SURS email and saves it as a PNG file.
    """
    # 1. Ensure the output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. Configure the QR code appearance and data density
    qr = qrcode.QRCode(
        version=1, # 1 is the smallest/simplest QR code format
        error_correction=qrcode.constants.ERROR_CORRECT_H, # High error correction (good for phone screens!)
        box_size=10, # Size of each little black square
        border=4, # White border thickness
    )

    # 3. Add the student's email as the hidden data
    qr.add_data(surs_mail)
    qr.make(fit=True)

    # 4. Generate the image file
    img = qr.make_image(fill_color="black", back_color="white")

    # 5. Create a safe filename (replace @ and . to avoid file system issues)
    safe_filename = surs_mail.replace("@", "_at_").replace(".", "_") + ".png"
    file_path = os.path.join(output_folder, safe_filename)

    # 6. Save the image
    img.save(file_path)
    print(f"✅ Success: Generated QR code for {surs_mail} -> Saved to {file_path}")

# --- Main Execution ---
if __name__ == "__main__":
    # Let's test it with a few sample committee members/students
    test_students = [
        "student_1@surs.pdn.ac.lk",
        "student_2@surs.pdn.ac.lk",
        "john.doe@surs.pdn.ac.lk"
    ]

    print("Starting QR Code Generation...")
    for student in test_students:
        create_student_qr(student)
    
    print("All QR codes generated successfully!")