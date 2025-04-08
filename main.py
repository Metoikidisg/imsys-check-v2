import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="§14a Imsys-Prüfung", layout="centered")

# Logo einfügen (oben links)
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.PNG", width=80)
with col2:
    st.title("🔌 §14a Imsys-Einbauprüfung – Optimiert")

st.markdown("---")

# Sidebar-Navigation
option = st.sidebar.radio("📂 Navigation", ["Einzelfallprüfung", "Anleitung"])

if option == "Einzelfallprüfung":
    st.subheader("📇 Kundendaten erfassen")
    with st.form("kundendaten_form"):
        col1, col2 = st.columns(2)
        with col1:
            vorname = st.text_input("Vorname")
            adresse = st.text_input("Adresse")
        with col2:
            nachname = st.text_input("Nachname")
            zaehlernummer = st.text_input("Zählernummer")

        submitted = st.form_submit_button("Daten speichern")
        if submitted:
            st.success(f"✅ Kundendaten gespeichert für {vorname} {nachname}, Zähler: {zaehlernummer}")

    st.markdown("---")
    # Schritt 1: Abfrage, ob Anlage vorhanden ist
    anlage = st.radio("🔧 Ist eine steuerbare Anlage vorhanden?", ["Ja", "Nein"], horizontal=True)

    anlage_typen = []
    verbrauch_jahre = []
    einbaudatum = None
    urteil = ""

    if anlage == "Ja":
        st.subheader("⚙️ Anlagenauswahl & technische Eckdaten")
        anlage_typen = st.multiselect(
            "Welche Anlagen sind vorhanden?",
            ["PV-Anlage", "Wallbox", "Stromspeicher", "PV + Speicher", "Wärmepumpe"]
        )

        if anlage_typen:
            leistung = st.number_input("Gesamtleistung der Anlage (in kW)", min_value=0.0, step=0.1)
            steuerbar = st.radio("Ist die Anlage steuerbar (z. B. über Steuerbox)?", ["Ja", "Nein"], horizontal=True)
            einbaudatum = st.date_input("Geplantes Inbetriebnahmedatum", value=date.today())
            fristdatum = einbaudatum + timedelta(days=730)

            st.markdown(f"📅 **Frist für Bereitstellung des CLS-Moduls durch MSB:** `{fristdatum.strftime('%d.%m.%Y')}`")

            if leistung <= 4.2:
                urteil = "30 EUR Rechnung"
                st.warning("⚠️ Leistung ≤ 4,2 kW – Rechnung über 30 EUR erforderlich.")
            elif leistung <= 30:
                if steuerbar == "Ja":
                    urteil = "Kein Rechnungserfordernis"
                    st.success("✅ Kein Rechnungserfordernis – steuerbare Anlage unter 30 kW.")
                else:
                    urteil = "30 EUR Rechnung"
                    st.warning("⚠️ Anlage nicht steuerbar – 30 EUR Rechnung erforderlich.")
            else:
                urteil = "Über 30 kW – Netzprüfung erforderlich"
                st.error("❌ Leistung > 30 kW – bitte Rücksprache mit Netzbetreiber halten!")

    elif anlage == "Nein":
        st.subheader("🔢 Manuelle Eingabe der Jahresverbräuche")
        jahr1 = st.number_input("Verbrauch vor 3 Jahren (in kWh)", min_value=0, step=100)
        jahr2 = st.number_input("Verbrauch vor 2 Jahren (in kWh)", min_value=0, step=100)
        jahr3 = st.number_input("Verbrauch letztes Jahr (in kWh)", min_value=0, step=100)

        if jahr1 and jahr2 and jahr3:
            verbrauch_jahre = [jahr1, jahr2, jahr3]
            durchschnitt = sum(verbrauch_jahre) / 3
            st.write(f"🔎 Durchschnittsverbrauch: **{durchschnitt:.0f} kWh/Jahr**")

            df = pd.DataFrame({
                "Jahr": ["Vor 3 Jahren", "Vor 2 Jahren", "Letztes Jahr"],
                "Verbrauch (kWh)": verbrauch_jahre
            })

            fig = px.bar(df, x="Jahr", y="Verbrauch (kWh)", title="📊 Verbrauchsentwicklung")
            st.plotly_chart(fig)

            if durchschnitt >= 6000:
                urteil = "Kein Einbau erforderlich"
                st.success("✅ Kein Einbau erforderlich – Verbrauch ausreichend hoch.")
            else:
                urteil = "30 EUR Rechnung"
                st.error("❌ Verbrauch unter 6000 kWh – Rechnung über 30 EUR erforderlich.")

    # Exportfunktion (nur wenn Kundendaten vorhanden sind)
    if submitted and urteil:
        export_df = pd.DataFrame([{
            "Vorname": vorname,
            "Nachname": nachname,
            "Adresse": adresse,
            "Zählernummer": zaehlernummer,
            "Ergebnis": urteil
        }])

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            export_df.to_excel(writer, index=False, sheet_name='Ergebnis')

        st.download_button(
            label="📥 Ergebnis als Excel herunterladen",
            data=buffer.getvalue(),
            file_name=f"Imsys_Ergebnis_{zaehlernummer}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif option == "Anleitung":
    st.header("📋 Anleitung zur Nutzung des Tools")
    st.markdown("""
    Dieses Tool dient zur Prüfung der Einbaupflicht eines intelligenten Messsystems gemäß §14a EnWG.

    **So funktioniert es:**
    - Wähle in der Sidebar "Einzelfallprüfung"
    - Gib Kundendaten ein
    - Entscheide, ob eine steuerbare Anlage vorhanden ist
    - Gib je nach Auswahl die Anlagendaten oder Verbrauchswerte ein
    - Das Tool berechnet automatisch das Ergebnis
    - Am Ende kannst du das Ergebnis als Excel exportieren

    Weitere Funktionen wie Massendatenprüfung, Rechnungserzeugung etc. folgen in Kürze 🚀
    """)
