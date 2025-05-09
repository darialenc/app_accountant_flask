from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

class Manager:
    def __init__(self):
        self.saldo = 0.0
        self.historia = []
        self.magazyn = {}
        self.saldo_file = "Saldo.txt"
        self.magazyn_file = "Magazyn.txt"
        self.historia_file = "Historia.txt"
        self.load_data()

    def load_data(self):
        self.saldo = self.load_saldo_from_file()
        self.magazyn = self.load_magazyn_from_file()
        self.historia = self.load_historia_from_file()

    def save_saldo_to_file(self):
        with open(self.saldo_file, "w", encoding="utf-8") as f:
            f.write(str(self.saldo))

    def save_magazyn_to_file(self):
        with open(self.magazyn_file, "w", encoding="utf-8") as f:
            for nazwa, produkt in self.magazyn.items():
                f.write(f"{nazwa},{produkt['ilosc']},{produkt['cena']}\n")

    def save_historia_to_file(self):
        with open(self.historia_file, "w", encoding="utf-8") as f:
            for wpis in self.historia:
                f.write(wpis + "\n")

    def load_saldo_from_file(self):
        if not os.path.exists(self.saldo_file):
            return 0.0
        with open(self.saldo_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return float(content) if content else 0.0

    def load_magazyn_from_file(self):
        magazyn = {}
        if not os.path.exists(self.magazyn_file):
            return magazyn
        with open(self.magazyn_file, "r", encoding="utf-8") as f:
            for line in f:
                nazwa, ilosc, cena = line.strip().split(",")
                magazyn[nazwa] = {"ilosc": int(ilosc), "cena": float(cena)}
        return magazyn

    def load_historia_from_file(self):
        if not os.path.exists(self.historia_file):
            return []
        with open(self.historia_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f]

manager = Manager()

@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "saldo":
            wartosc = float(request.form.get("wartosc", 0))
            manager.saldo += wartosc
            manager.historia.append(f"Zmiana salda: {wartosc} PLN")
            manager.save_saldo_to_file()

        elif action == "zakup":
            nazwa = request.form.get("nazwa")
            cena = float(request.form.get("cena"))
            ilosc = int(request.form.get("ilosc"))
            koszt = cena * ilosc
            if koszt <= manager.saldo:
                manager.saldo -= koszt
                if nazwa in manager.magazyn:
                    manager.magazyn[nazwa]["ilosc"] += ilosc
                else:
                    manager.magazyn[nazwa] = {"ilosc": ilosc, "cena": cena}
                manager.historia.append(f"Zakup: {nazwa}, {ilosc} szt. po {cena} PLN")
            else:
                manager.historia.append(f"Nieudany zakup: {nazwa}, brak środków")

        elif action == "sprzedaz":
            nazwa = request.form.get("nazwa")
            ilosc = int(request.form.get("ilosc"))
            if nazwa in manager.magazyn and manager.magazyn[nazwa]["ilosc"] >= ilosc:
                cena = manager.magazyn[nazwa]["cena"]
                manager.saldo += cena * ilosc
                manager.magazyn[nazwa]["ilosc"] -= ilosc
                if manager.magazyn[nazwa]["ilosc"] == 0:
                    del manager.magazyn[nazwa]
                manager.historia.append(f"Sprzedaż: {nazwa}, {ilosc} szt. po {cena} PLN")
            else:
                manager.historia.append(f"Nieudana sprzedaż: {nazwa}")

        manager.save_saldo_to_file()
        manager.save_magazyn_to_file()
        manager.save_historia_to_file()
        return redirect(url_for("main"))

    return render_template("main.html", saldo=manager.saldo, magazyn=manager.magazyn)

@app.route("/historia/")
@app.route("/historia/<int:start>/<int:end>/")
def historia(start=0, end=None):
    historia = manager.historia
    if end is None:
        end = len(historia)

    if start < 0 or end > len(historia) or start >= end:
        error_msg = f"Błędny zakres. Możliwy zakres: 0 - {len(historia)}"
        return render_template("historia.html", historia=[], od=start, do=end, error=error_msg)

    historia_fragment = historia[start:end]
    return render_template("historia.html", historia=historia_fragment, od=start, do=end, error=None)

if __name__ == "__main__":
    app.run(debug=True)
