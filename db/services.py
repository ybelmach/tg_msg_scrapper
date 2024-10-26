from db import models
from schemas import Channel, Message


# def creating_id(db, data: Channel):
#     new_post = models.Channels(**data.model_dump())
#     db.add(new_post)
#     db.commit()
#     db.refresh(new_post)  # Чтобы получить возвращаемое значение из БД
#     return new_post


def updating_id(db, data: Channel):
    post_querry = db.query(models.Channels).filter(models.Channels.id == str(data.id))  # Убрать str
    if post_querry.first() is None:
        raise Exception(f"Post {data.id} was not found")
    post_querry.update(data.model_dump(), synchronize_session=False)
    db.commit()


def adding_msg(db, data: Message):
    new_msg = models.Messages(**data.model_dump())
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg
