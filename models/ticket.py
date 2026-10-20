class Ticket:
     def __init__(self, ticket_id: int, title: str, description: str, priority: str = "Medium"):
         self.ticket_id = ticket_id
         self.title = title
         self.description = description 
         self.priority = priority 
         self.status = "Open"
def update_status(self, new_status: str):
    allowed_statuses = ["Open", "In Progress", "Closed"]
    if new_status in allowed_statuses:
        self.status = new_status
        print(f"Bilet #{self.ticket_id} durumu güncellendi: {self.status}")
    else:
        print(f"Geçersiz durum! Kullanılabilir durumlar: {allowed_statuses}")

def get_details(self) -> dict:
    return {
        "ID": self.ticket_id,
        "Title": self.title,
        "Description": self.description,
        "Priority": self.priority,
        "Status": self.status
    }