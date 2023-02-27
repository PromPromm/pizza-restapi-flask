from ..utils import db
from enum import Enum
from datetime import datetime


class Sizes(Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    EXTRA_LARGE = 'extra_large'


class OrderStatus(Enum):
    PENDING = 'pending'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'

class OrderFlavour(Enum):
    BBQ_CHICKEN = 'bbq_chicken'
    PEPPERONI = 'pepperoni'
    SAUSAGE = 'sausage'
    CHEESE = 'cheese'
    EXTRA_CHEESE = 'extra_cheese'
    BACON = 'bacon'
    PINEAPPLE = 'pineapple'
    MARGHERITA = 'margherita'


class Order(db.Model):
    __tablename__='orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sizes = db.Column(db.Enum(Sizes), default=Sizes.SMALL)
    quantity = db.Column(db.Integer, default=1)
    order_status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    flavour = db.Column(db.Enum(OrderFlavour), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    customer = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Order {self.id}>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def delete_by_id(self):
        db.session.delete(self)
        db.session.commit()