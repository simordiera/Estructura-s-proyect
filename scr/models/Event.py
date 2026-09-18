class Event:

    def __init__(self, id , magnitude, depth,epicenter, datetime, review, stations, attention_status):
        self.set_id(id)
        self.set_magnitude(magnitude)
        self.set_depth(depth)
        self.set_epicenter(epicenter[0], epicenter[1])
        
        self.set_datetime = datetime
        self.set_review = review
        self.set_stations = stations
        self.set_attention_status = attention_status

        self.set_zone()
        self.set_priority()

        
    def set_id (self, id):
        if (id>=1 and id<=999999):
            self._id=id
            return True
        return False

    def get_id(self):
        id=self._id
        return id

    def set_magnitude (self, M):
        if (M>=-2.0 and M<=10.0):
            self._magnitude=M
            return True
        return False

    def get_magnitude (self):
        M=self._magnitude
        return M
    
    def set_depth(self, H):
        if (H>=0.0 and H<=700.0):
            self._depth=H
            return True
        return False

    def get_depth (self):
        H=self._depth
        return H

    def set_epicenter(self, x, y):
        if (0.0<=x<=1000.0 and 0.0<=y<=1000.0):
            self._epicenter=(x,y)
            return True
        return False
    
    def get_epicenter(self):
        epicenter=self._epicenter
        return epicenter

    def set_zone(self):
        if self._epicenter:
            x=self._epicenter[0]
            y=self._epicenter[1]
            if (0.0<=x<=500.0 and 0.0<=y<=500.0):
                self._zone="no poblada"
                return True
            elif (500.0<x<=1000.0 and 500.0<= y<=1000.0):
                self._zone="poblada"
                return True
        return False
    def get_zone(self):
        zone=self._zone
        return zone

    def set_priority(self):
        if self._magnitude: 
            M=self._magnitude
        if self._depth:
            H=self._depth            
        if M and H:
            if self._zone=="poblada" or self._zone=="no poblada":
                if (M>=6.0):
                    self._priority=3
                elif (M>=4.5 and H<=30.0 and self._zone=="poblada"):
                    self._priority=3
                elif (M>=4.5):
                    self._priority=2
                else:
                    self._priority=1
    def get_priority(self):
        priority=self._priority
        return priority

    def get_code(self):
        p=self._priority
        M=self._magnitude
        id=self._id
        return (p, M, id)

    def __str__(self):
        return str(self.__dict__)