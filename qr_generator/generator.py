"""Generate QR code images for SURS student emails.

Each QR code encodes the student's email address. The generated PNG files are
saved into an output folder, with a filename derived from the email.
"""

import os

import qrcode


def create_student_qr(surs_mail: str, output_folder: str = "output"):
    """Create a QR code PNG file for a single student email."""

    # Ensure the output directory exists.
    os.makedirs(output_folder, exist_ok=True)

    # Configure the QR code generator.
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    # Encode the email address as the QR payload.
    qr.add_data(surs_mail)
    qr.make(fit=True)

    # Generate the image and persist it.
    img = qr.make_image(fill_color="black", back_color="white")

    safe_filename = surs_mail.replace("@", "_at_").replace(".", "_") + ".png"
    file_path = os.path.join(output_folder, safe_filename)

    img.save(file_path)
    print(f"Generated QR code for {surs_mail} -> {file_path}")


if __name__ == "__main__":
    # Example usage: generate a handful of QR codes for testing.
    test_students = [
        "student_1@surs.pdn.ac.lk",
        "student_2@surs.pdn.ac.lk",
        "john.doe@surs.pdn.ac.lk",
    ]

    print("Generating sample QR codes...")
    for student in test_students:
        create_student_qr(student)

    print("Done.")
