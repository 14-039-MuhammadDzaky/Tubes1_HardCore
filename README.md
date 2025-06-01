# Tubes1_HardCore
Strategi greedy yang dipilih untuk implementasi dalam program bot ini adalah strategi value per distance, yaitu memilih objek dengan nilai terbagi jarak tertinggi. Strategi ini dilengkapi dengan kondisi khusus untuk kembali ke base ketika inventaris penuh, dan menuju tombol merah apabila tidak ada diamond dalam radius tertentu. Strategi ini dipilih karena memberikan hasil yang konsisten baik dari segi efisiensi gerakan maupun jumlah poin yang dikumpulkan. Selain itu, strategi ini mudah diimplementasikan dan cukup adaptif terhadap perubahan kondisi permainan

langkah-langkah 
1. download file github.
2. setelah itu, ekstrak file yang telah download
3. copy file HcBot.py kedalam game/logic/..
4. kemudia buka main.py, modifikasi pada controller menjadi "CONTROLLERS = {"Random": RandomLogic, "HcBot": HcBot,}" lalu save
5. kemudian, jalankan pada terminal dengan perintah "python main.py --logic HcBot --email=HcBot@email.com --name=HcBot123 --password=123 --team HardCore"

Author :
1. Muhammad Dzaky_123140039
2. Muhammad Farhan Muzakhi_123140075
3. Bonifasius Ezra Mariano_123140196

