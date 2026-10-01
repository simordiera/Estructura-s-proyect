from datetime import datetime
class Event:

    def __init__(self, id, magnitude, depth, epicenter, datetime, station,
                 attention_status="Pendiente", revisions=None):
        self.set_id(id)
        self.set_magnitude(magnitude)
        self.set_depth(depth)
        self.set_epicenter(epicenter[0], epicenter[1])
        
        self.set_datetime(datetime)
        self.set_station(station)

        self.set_zone()
        self.set_priority()

        self.set_review(0)

        if revisions is None:
            self.set_revisions(1)
        else:
            self.set_revisions(revisions)

    def set_review(self, review):
        self.review = review

    def get_review(self):
        review=self.review
        return review

    def set_revisions(self, revisions):
        self.revisions = revisions

    def get_revisions(self):
        revisions=self.revisions
        return revisions   
     
    def set_datetime(self, date):
        date = datetime.fromisoformat(date)
        today = datetime.now()

        if date > today:
            return False

        self.datetime = date
        return True

    def get_datetime(self):
        return self.datetime

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
        if (0<=x<=1000 and 0<=y<=1000):
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
            distance=1000/10 #10 in x and 10 in y. 1000/10=100, in total is 100 tile
            populated_area_x=[100,300,600,800,200,500,700,100,200,500,800,200,500,700,900,100,400,700, 0,900]
            populated_area_y=[0,0,0,100,200,200,300,400,400,400,500,600,600,600,700,800,800,800,900,900]

            for i in range(len(populated_area_x)):
                if (populated_area_x[i]<=x<=(populated_area_x[i]+distance) and populated_area_y[i]<=y<=populated_area_y[i]+distance):
                    self._zone="poblada"
                    return True
            
            self._zone="no poblada"
            return True 
                
        
    def get_zone(self):
        zone=self._zone
        return zone

    def set_priority(self):
        M=self._magnitude
        H=self._depth
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

    def set_station(self, station):
        self._station=station

    def get_station(self):
        station=self._station
        return station

    def __str__(self):
        return f"({self._priority},{self._magnitude},{self._id})"+str(self.__dict__)