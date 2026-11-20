import tree_sitter_python as tspython
from tree_sitter import Language, Parser

def run_tugas1():
    PY_LANGUAGE = Language(tspython.language())
    parser = Parser(PY_LANGUAGE)

    print("=" * 70)
    print("TUGAS 1: MEMBACA POHON SINTAKS (TREE-SITTER)")
    print("=" * 70)

    # 1. Tiga Potongan Kode Python
    snippets = {
        "1. Fungsi": b"""def hitung_diskon(harga, persen):
    return harga * (1 - persen / 100)
""",
        "2. If/Else": b"""if nilai >= 75:
    status = "Lulus"
else:
    status = "Remidi"
""",
        "3. Kelas dengan Satu Method": b"""class Rekening:
    def setor(self, jumlah):
        self.saldo += jumlah
"""
    }

    # Perkiraan Pohon Tulisan Tangan / Teoretis vs Hasil Sebenarnya
    prediksi = {
        "1. Fungsi": "(module (function_definition name: (identifier) parameters: (parameters (identifier) (identifier)) body: (block (return_statement (binary_operator left: (identifier) right: (parenthesized_expression (binary_operator left: (integer) right: (binary_operator left: (identifier) right: (integer)))))))))",
        "2. If/Else": "(module (if_statement condition: (comparison_operator left: (identifier) operator: \">=\" right: (integer)) consequence: (block (expression_statement (assignment left: (identifier) right: (string)))) alternative: (else_clause (block (expression_statement (assignment left: (identifier) right: (string)))))))",
        "3. Kelas dengan Satu Method": "(module (class_definition name: (identifier) body: (block (function_definition name: (identifier) parameters: (parameters (identifier) (identifier)) body: (block (expression_statement (augmented_assignment left: (attribute) right: (identifier))))))))"
    }

    for judul, kode in snippets.items():
        print(f"\n--- Potongan {judul} ---")
        print("Kode Sumber:")
        print(kode.decode().strip())
        print("\n[Perkiraan Pohon (Mental Model)]:")
        print(prediksi[judul])
        
        tree = parser.parse(kode)
        print("\n[Pohon Sebenarnya (tree.root_node)]:")
        print(tree.root_node)

    # 2. Perbedaan Node Bernama vs Node Anonim
    print("\n" + "=" * 70)
    print("PEMERIKSAAN NODE BERNAMA VS NODE ANONIM PADA FUNGSI")
    print("=" * 70)
    fn_code = snippets["1. Fungsi"]
    fn_tree = parser.parse(fn_code)
    fn_node = fn_tree.root_node.children[0]  # function_definition

    print(f"Parent Node: {fn_node.type} (is_named: {fn_node.is_named})")
    print("\nSemua children (node.children) - mencakup node anonim:")
    for i, child in enumerate(fn_node.children):
        status = "BERNAMA" if child.is_named else "ANONIM"
        field = fn_node.field_name_for_child(i)
        field_str = f" [field: {field}]" if field else ""
        print(f"  [{i}] type: {child.type:<22} status: {status:<8} text: {repr(child.text.decode())}{field_str}")

    print("\nHanya named_children (node.named_children) - node anonim disaring:")
    for i, child in enumerate(fn_node.named_children):
        print(f"  [{i}] type: {child.type:<22} text: {repr(child.text.decode())}")

    print("\nContoh Node Anonim tersembunyi yang ditemukan:")
    print("  1. 'def'  -> keyword pendefinisian fungsi (node anonim string literal)")
    print("  2. ':'    -> titik dua pembuka blok kode")
    print("  3. '('    -> kurung buka pada daftar parameter (di dalam parameters)")
    print("  4. ')'    -> kurung tutup pada daftar parameter")
    print("  5. '*'    -> operator aritmetika perkalian")

    # 3. Pengujian Error Recovery (Sintaks Rusak)
    print("\n" + "=" * 70)
    print("PENGUJIAN ERROR RECOVERY (SINTAKS RUSAK)")
    print("=" * 70)

    # Kasus A: Hilang titik dua (:) pada def
    kode_rusak_1 = b"def sapa(nama)\n    return nama\n"
    print("\nKasus A: Hilang tanda ':' pada def")
    print("Kode: def sapa(nama) \\n return nama")
    tree_rusak_1 = parser.parse(kode_rusak_1)
    print("Pohon hasil parse:")
    print(tree_rusak_1.root_node)
    print("Has Error:", tree_rusak_1.root_node.has_error)

    # Kasus B: Hilang kurung tutup ')' pada parameter
    kode_rusak_2 = b"def sapa(nama:\n    return nama\n"
    print("\nKasus B: Hilang kurung tutup ')' pada parameter")
    print("Kode: def sapa(nama: \\n return nama")
    tree_rusak_2 = parser.parse(kode_rusak_2)
    print("Pohon hasil parse:")
    print(tree_rusak_2.root_node)
    print("Has Error:", tree_rusak_2.root_node.has_error)

if __name__ == "__main__":
    run_tugas1()
