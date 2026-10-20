# IF3170_G18_YuzukiAkatsuki

Repositori ini berisi Tugas Besar 1 IF3170 Inteligensi Artifisial 2026/2027 (G18_YuzukiAkatsuki)

<img width="1920" height="1080" alt="Add a heading (2)" src="https://github.com/user-attachments/assets/2731a4ac-943f-4d90-b28c-a444a937bb33" />


Program ini menyelesaikan persoalan **Mejiro Express**: memilih dan menata paket (kubus/balok) di dalam sebuah peti kemas truk agar **total value paket yang diangkut maksimum**, tanpa melanggar batasan fisik (tidak menembus dinding, tidak saling tumpang tindih, tidak melayang, paket fragile tidak boleh menjadi penyangga, dan total berat tidak melebihi kapasitas). Persoalan diselesaikan dengan algoritma *local search* dalam Python:

- Steepest Ascent Hill-climbing (`steepest`)
- Hill-climbing with Sideways Move (`sideways`)
- Random Restart Hill-climbing (`random_restart`)
- Stochastic Hill-climbing (`stochastic`)
- Simulated Annealing (`sa`)
- Genetic Algorithm (`ga`)

## Struktur Repository

```
.
├── src/                  source code
│   ├── main.py           program utama
│   ├── experiment.py     pengulangan run dan skenario eksperimen GA
│   ├── view_state.py     melihat ulang state hasil run dalam plot 3D interaktif
│   ├── algorithms/       algoritma local search
│   ├── core/             state, neighbor, objective function, I/O
│   ├── visualization/    plot state 3D, objective vs iterasi, e^(ΔE/T)
│   └── data/             contoh input 
├── data/                 data uji (30, 40, 50, dan 100 paket)
├── docs/                 laporan (.pdf)
├── output/               hasil run (JSON dan gambar)
├── requirements.txt
└── README.md
```

## Setup

Dibutuhkan Python 3.11 atau lebih baru (dikembangkan dan diuji dengan Python 3.11.9).

```
pip install -r requirements.txt
```

Satu-satunya dependensi tambahan adalah `matplotlib`.

## Cara Menjalankan

Seluruh perintah dijalankan dari folder `src`:

```
cd src
```

Contoh untuk tiap algoritma (3 run per perintah):

```
python main.py --input ../data/input_50_paket.json --algo steepest --seed 1
python main.py --input ../data/input_50_paket.json --algo sideways --max-sideways 50 --seed 1
python main.py --input ../data/input_50_paket.json --algo random_restart --max-restart 5 --seed 1
python main.py --input ../data/input_50_paket.json --algo stochastic --max-iterations 10000 --seed 1
python main.py --input ../data/input_50_paket.json --algo sa --max-iterations 5000 --seed 1
python main.py --input ../data/input_50_paket.json --algo ga --population 50 --max-iterations 100 --seed 1
```

Seluruh skenario eksperimen Genetic Algorithm (variasi populasi dan banyak iterasi, masing-masing 3 run):

```
python main.py --input ../data/input_50_paket.json --ga-experiment --seed 1
```

### Opsi

| Opsi | Keterangan |
|---|---|
| `--input` | Berkas JSON persoalan (wajib) |
| `--algo` | `steepest`, `sideways`, `random_restart`, `stochastic`, `sa`, atau `ga` |
| `--runs` | Banyak run, default 3 |
| `--seed` | Seed awal; run ke-i memakai seed + i sehingga hasil dapat diulang |
| `--no-plot` | Tidak membuat plot |
| `--show` | Menampilkan plot secara interaktif (tanpa opsi ini, plot hanya disimpan) |
| `--objective` | `value` (default, total value) atau `density` (total value / berat paket) |
| `--max-sideways` | Batas sideways move (Hill-climbing with Sideways Move) |
| `--max-restart` | Batas restart (Random Restart Hill-climbing) |
| `--max-iterations` | Banyak iterasi (Stochastic HC, Simulated Annealing, Genetic Algorithm) |
| `--population` | Jumlah populasi (Genetic Algorithm) |
| `--initial-temp`, `--min-temp` | Suhu awal dan suhu minimum (Simulated Annealing), default 1000 dan 0,001 |
| `--stuck-patience` | K untuk menghitung stuck pada Simulated Annealing, default 100 |

### Format Input

```json
{
  "truck": { "dimensions": { "w": 10, "l": 20, "h": 5 }, "max_capacity": 500 },
  "packages": [
    { "id": "P01", "dimensions": { "w": 3, "l": 4, "h": 1 },
      "value": 60, "weight": 5, "is_fragile": false, "eta": 3 }
  ]
}
```

Dimensi dan koordinat berupa bilangan bulat. Contoh berkas ada di folder `data/`.

### Hasil Run

Setiap run menyimpan satu berkas JSON (state awal dan akhir, nilai objective, riwayat objective, durasi, dan data khusus algoritma) beserta gambar `*_initial.png`, `*_final.png`, `*_history.png`, di folder `output/`. Ringkasan tiap run dicetak di terminal.

## Pembagian Tugas

| NIM | Nama | Pembagian |
|---|---|---|
| 13524012 | Tengku Naufal Saqib | Hill Climbing |
| 13524039 | Rhenaldy Cahyadi Putra | Simulated Annealing |
| 13524113 | Fauzan Mohamad Abdul Ghani | Genetic Algorithm |

Made with 💚 by YuzukiAkatsuki
