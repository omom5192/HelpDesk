from models.ticket import Ticket
#Deneme icin yeni bir bilet olusturma
ticket1 = Ticket(ticket_id=101, title="Bilgisayar ekrani calismiyor", description="Acilista ekran tamamen siyah", priority="High")
#Bilet detaylarini goruntuleme
print("--- Bilet Detaylari ---") 
print(ticket1.get_details())
print("\n--- Durum Guncelleme Testi ---")
#Durumu gecerli bir degere guncelleme
ticket1.update_status("In Progress")
#Gecersiz bir durum denemesi
ticket1.update_status("Done")