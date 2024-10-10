Submission Dicoding "Belajar Analisis Data dengan Python" - Bangkit 2024
Deskripsi
Analisis ini bertujuan untuk mengeksplorasi dataset E-Commerce publik sebagai bagian dari program Bangkit 2024.

Struktur Direktori
/Dataset: File data .csv untuk analisis.
/Dashboard: File Dashboard.py untuk dashboard Streamlit.
Notebook.ipynb: Jupyter Notebook untuk analisis eksploratif.
Setup Environment
1. Mount Google Drive
python
Copy code
from google.colab import drive
drive.mount('/content/drive')
2. Install Streamlit
bash
Copy code
!pip install streamlit -q
3. Jalankan Streamlit
bash
Copy code
!wget -q -O - ipv4.icanhazip.com
!streamlit run Dashboard.py & npx localtunnel --port 8501
