# 🛰️ VALOSINT CHECKER ID

VALOSINT CHECKER ID is a Python-based security auditing tool designed for account testing and educational purposes.  
This tool simulates login requests while using proxy rotation and CSRF handling to mimic real authentication systems.

---

## 🚀 Features

- Satellite scanning style terminal interface  
- Automatic proxy rotation (1 proxy per request)  
- Multi-threaded account checking  
- Auto-save valid results to `results/` folder  
- Live timestamp logging for every attempt  

---

## 🛠 Installation

Clone this repository

```
git clone https://github.com/Abhsith/VALOSINT-CHECKER-ID.git
cd VALOSINT-CHECKER-ID
```

Install requirements

```
pip install -r requirements.txt
```

---

## ⚙️ Usage

Run the tool

```
python checker.py
```

Prepare these files before running

- combo.txt → email:password list  
- proxies.txt → proxy list

Example combo format

```
email@example.com:password123
user@mail.com:qwerty
```

---

## 📁 Project Structure

```
VALOSINT-CHECKER-ID
│
├── checker.py
├── combo.txt
├── proxies.txt
├── results/
├── requirements.txt
└── README.md
```

---

## ⚠️ Disclaimer

This project is for **educational and security research purposes only**.  
The developer is not responsible for misuse of this tool.

---

## 👨‍💻 Author

Abhsith  
https://github.com/Abhsith
