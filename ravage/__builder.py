import os
import zipfile


def build_zip() -> bytes:
    ravage_path = os.path.dirname(__file__)
    fn = 'ravage.zip'
    zf = zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(ravage_path):
        for file in files:
            if '__pycache__' not in root and file != os.path.basename(__file__):
                zf.write(os.path.join(root, file), arcname=os.path.join(os.path.relpath(root, ravage_path), file))
    zf.close()

    with open(fn, 'rb') as fh:
        c = fh.read(1)
        data = b''
        while True:
            data += c
            if not c:
                break
            c = fh.read(1)
    os.unlink(fn)
    return data
