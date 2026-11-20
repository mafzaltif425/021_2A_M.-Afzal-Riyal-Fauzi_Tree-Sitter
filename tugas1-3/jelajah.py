import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))

def jelajah_rekursif(node, kedalaman=0, field=None):
    """
    Menelusuri pohon sintaks secara rekursif.
    Hanya mencetak node bernama (named), dengan indentasi sesuai kedalaman,
    tipe node, posisi [baris:kolom] (baris dimulai dari 1), serta field jika ada.
    """
    baris, kolom = node.start_point
    label = f"{field}: " if field else ""
    hasil = ["  " * kedalaman + f"{label}{node.type} [{baris + 1}:{kolom}]"]

    # Menelusuri semua child dengan enumerate agar indeks child akurat
    # untuk mengambil nama field melalui node.field_name_for_child(i)
    for i, child in enumerate(node.children):
        if not child.is_named:
            continue
        child_field = node.field_name_for_child(i)
        hasil.extend(jelajah_rekursif(child, kedalaman + 1, child_field))
    
    return hasil

def jelajah_cursor(tree):
    """
    [PENGAYAAN] Menelusuri pohon sintaks menggunakan TreeCursor.
    Menghasilkan urutan dan format yang identik dengan versi rekursif.
    """
    cursor = tree.walk()
    hasil = []
    kedalaman = 0

    while True:
        node = cursor.node
        if node.is_named:
            baris, kolom = node.start_point
            field = cursor.field_name
            label = f"{field}: " if field else ""
            hasil.append("  " * kedalaman + f"{label}{node.type} [{baris + 1}:{kolom}]")

        # Coba turun ke anak pertama
        if cursor.goto_first_child():
            if node.is_named:
                kedalaman += 1
            continue

        # Jika tidak punya anak, coba pindah ke saudara (sibling)
        if cursor.goto_next_sibling():
            continue

        # Jika tidak punya saudara, naik ke parent sampai menemukan saudara berikutnya
        found_sibling = False
        while cursor.goto_parent():
            parent_node = cursor.node
            if parent_node.is_named:
                kedalaman -= 1
            if cursor.goto_next_sibling():
                found_sibling = True
                break

        if not found_sibling:
            break

    return hasil

def main():
    if len(sys.argv) < 2:
        print("Penggunaan: python jelajah.py <file.py> [--cursor | --compare]")
        sys.exit(1)

    file_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "--rekursif"

    with open(file_path, "rb") as f:
        content = f.read()

    tree = parser.parse(content)

    if mode == "--compare":
        out_rec = jelajah_rekursif(tree.root_node)
        out_cur = jelajah_cursor(tree)
        print(f"Total node rekursif: {len(out_rec)}")
        print(f"Total node TreeCursor: {len(out_cur)}")
        is_identik = (out_rec == out_cur)
        print(f"Apakah hasil Rekursif dan TreeCursor IDENTIK? -> {is_identik}")
        if not is_identik:
            for idx, (r, c) in enumerate(zip(out_rec, out_cur)):
                if r != c:
                    print(f"Beda pada indeks {idx}:")
                    print(f"  Rekursif : {r}")
                    print(f"  Cursor   : {c}")
                    break
        else:
            print("Perbandingan Sukses: Output kedua metode 100% cocok.")
            print("\nCuplikan 25 baris pertama:")
            for line in out_rec[:25]:
                print(line)
    elif mode == "--cursor":
        for line in jelajah_cursor(tree):
            print(line)
    else:  # default rekursif
        for line in jelajah_rekursif(tree.root_node):
            print(line)

if __name__ == "__main__":
    main()
