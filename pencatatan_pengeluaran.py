"""
Sistem Pencatatan Pengeluaran Harian Mahasiswa dan Batas Anggaran
Prototipe berbasis terminal (tanpa database, GUI, AI, atau web).

Cara pakai:
    python pencatatan_pengeluaran.py         -> menjalankan program
    python pencatatan_pengeluaran.py test    -> menjalankan pengujian
"""

import sys
from datetime import datetime

AMBANG_PERINGATAN = 0.8  # peringatan jika pengeluaran >= 80% batas harian


def rupiah(angka):
    """Memformat angka menjadi teks rupiah, contoh: Rp50.000."""
    return f"Rp{angka:,}".replace(",", ".")


def angka_positif(teks):
    """True jika teks hanya berisi angka 0-9 dan nilainya lebih dari 0."""
    return teks.isascii() and teks.isdigit() and int(teks) > 0


def total_hari(data, tanggal):
    """Menjumlahkan semua pengeluaran pada satu tanggal."""
    total = 0
    for item in data:  # proses berulang
        if item["tanggal"] == tanggal:
            total += item["nominal"]
    return total


def catat_pengeluaran(data, tanggal, kategori, nominal_teks, batas):
    """Memvalidasi input, menyimpan pengeluaran, lalu memeriksa batas anggaran.
    Mengembalikan (status, pesan)."""
    tanggal = tanggal.strip()
    nominal_teks = nominal_teks.strip()

    # Keputusan 1: apakah input lengkap?
    if tanggal == "" or kategori.strip() == "" or nominal_teks == "":
        return "DATA TIDAK LENGKAP", "Tanggal, kategori, dan nominal wajib diisi."

    # Keputusan 2: apakah format tanggal benar?
    try:
        datetime.strptime(tanggal, "%Y-%m-%d")
    except ValueError:
        return "FORMAT TANGGAL SALAH", "Gunakan format TTTT-BB-HH, contoh 2026-10-30."

    # Keputusan 3: apakah nominal berupa angka positif?
    if not angka_positif(nominal_teks):
        return "NOMINAL TIDAK VALID", "Nominal harus berupa angka lebih dari 0."

    nominal = int(nominal_teks)
    data.append({"tanggal": tanggal, "kategori": kategori.strip().lower(),
                 "nominal": nominal})

    # Keputusan 4: bandingkan total hari ini dengan batas anggaran
    total = total_hari(data, tanggal)
    if total > batas:
        return "MELEBIHI BATAS", f"Total {rupiah(total)} melebihi batas {rupiah(batas)}."
    elif total >= AMBANG_PERINGATAN * batas:
        return "PERINGATAN", f"Total {rupiah(total)} mendekati batas {rupiah(batas)}."
    else:
        return "AMAN", f"Total {rupiah(total)} masih di bawah batas {rupiah(batas)}."


def tampilkan_ringkasan(data, tanggal, batas):
    """Menampilkan daftar pengeluaran dan sisa anggaran pada satu tanggal."""
    tanggal = tanggal.strip()
    print(f"\nRingkasan {tanggal}")
    for item in data:
        if item["tanggal"] == tanggal:
            print(f"- {item['kategori']:<12} {rupiah(item['nominal'])}")
    total = total_hari(data, tanggal)
    print(f"Total : {rupiah(total)}")
    print(f"Sisa  : {rupiah(batas - total)}")


def jalankan_program():
    data = []  # penyimpanan sementara (list) selama program berjalan
    batas = 50000
    while True:  # proses berulang: menu tampil sampai pengguna keluar
        print("\n=== Pencatatan Pengeluaran Harian ===")
        print(f"Batas harian saat ini: {rupiah(batas)}")
        print("1. Catat pengeluaran\n2. Lihat ringkasan hari\n"
              "3. Ubah batas harian\n0. Keluar")
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            tanggal = input("Tanggal (TTTT-BB-HH): ")
            kategori = input("Kategori (makan/transport/dll): ")
            nominal = input("Nominal (Rp): ")
            status, pesan = catat_pengeluaran(data, tanggal, kategori, nominal, batas)
            print(f"[{status}] {pesan}")
        elif pilihan == "2":
            tampilkan_ringkasan(data, input("Tanggal (TTTT-BB-HH): "), batas)
        elif pilihan == "3":
            baru = input("Batas harian baru (Rp): ").strip()
            if angka_positif(baru):
                batas = int(baru)
            else:
                print("[NOMINAL TIDAK VALID] Batas harus angka lebih dari 0.")
        elif pilihan == "0":
            print("Terima kasih. Data tidak disimpan setelah program ditutup.")
            break
        else:
            print("Menu tidak dikenal, coba lagi.")


def jalankan_test():
    """Menjalankan test case dan mencetak tabel hasil."""
    batas = 50000
    awal = {"tanggal": "2026-10-30", "kategori": "makan", "nominal": 20000}
    kasus = [  # (nama, tanggal, kategori, nominal, status yang diharapkan)
        ("Pengeluaran normal (total 60%)", "2026-10-30", "transport", "10000", "AMAN"),
        ("Mendekati batas (total 80%)",    "2026-10-30", "makan",     "20000", "PERINGATAN"),
        ("Tepat di batas (total 100%)",    "2026-10-30", "makan",     "30000", "PERINGATAN"),
        ("Melebihi batas (total 110%)",    "2026-10-30", "belanja",   "35000", "MELEBIHI BATAS"),
        ("Tanggal kosong",                 "",           "makan",     "10000", "DATA TIDAK LENGKAP"),
        ("Format tanggal salah",           "30-10-2026", "makan",     "10000", "FORMAT TANGGAL SALAH"),
        ("Nominal bukan angka",            "2026-10-30", "makan",     "abc",   "NOMINAL TIDAK VALID"),
        ("Nominal nol",                    "2026-10-30", "makan",     "0",     "NOMINAL TIDAK VALID"),
    ]
    lulus = 0
    for no, (nama, tgl, kat, nom, harapan) in enumerate(kasus, start=1):
        data = [dict(awal)]  # data awal baru untuk setiap test case
        aktual, _ = catat_pengeluaran(data, tgl, kat, nom, batas)
        status = "Lulus" if aktual == harapan else "Gagal"
        lulus += status == "Lulus"
        print(f"{no} | {nama} | {harapan} | {aktual} | {status}")
    print(f"Hasil: {lulus}/{len(kasus)} test case lulus")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        jalankan_test()
    else:
        jalankan_program()
