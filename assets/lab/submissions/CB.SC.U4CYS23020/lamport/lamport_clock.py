class process:
    def __init__(self, name):
        self.name = name
        self.clock = 0
        
    def local_events(self , events_id):
        self.clock += 1
        return{"process": self.name,
               "events": events_id,
               "type":"local",
               "timestamp":self.clock
               }
    
    def send_events(self,events_id,receiver_name):
        self.clock += 1
        message ={"message_id":f"M_{events_id}" ,
               "sender": self.name,
               "receiver":receiver_name,
               "timestamp":self.clock
               }
        events_record ={"process": self.name,
               "events": events_id,
               "type":"send",
               "timestamp":self.clock
               }
        return message, events_record
    
    def receiver_events(self,events_id, message):
        self.clock = max(self.clock,message["timestamp"])+1
        return{"process": self.name,
               "events": events_id,
               "type":"receiver",
               "timestamp":self.clock
               }
def main():
    p1 = process("P1")
    p2 = process("P2")
    p3 = process("P3")
    events =[]
    events.append(p1.local_events("E1"))
    m1,e2 = p1.send_events("E2",p2.name)
    events.append(e2)
    events.append(p2.receiver_events("E3",m1))
    events.append(p2.local_events("E4"))
    m2,e5 = p2.send_events("E5",p3.name)
    events.append(e5)
    events.append(p1.local_events("E6"))
    m3,e7=p1.send_events("E7",p3.name)
    events.append(e7)
    events.append(p3.receiver_events("E8",m2))
    events.append(p3.receiver_events("E9",m3))
    print("====================================================")
    print("             LAMPORT LOGICAL CLOCK")
    print("====================================================")
    print("")
    print(f"{'Process':<10} {'events':<8} {'Type':<12} {'Timestamp':>10}")
    print("-" * 52)
    
    for e in events:
        print(f"{e['process']:<10} {e['events']:<8} {e['type']:<12} {e['timestamp']:>10}")
        
    print("-" * 52)

if __name__ == "__main__":
    main()
    
