from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,or_,and_
from app.models.dms import Dms,Dm_Messages
from app.models.servers import Server
from app.models.user import Users

async def check_already_created_dm(db:AsyncSession,current_user_username:str,remote_user_username:str):
    already_dm = await db.execute(
                                select(Dms).filter(
                                    or_(
                                        and_(Dms.sender == current_user_username,Dms.receiver == remote_user_username),
                                        and_(Dms.receiver == current_user_username,Dms.sender == remote_user_username)
                                        )
                                    )
                                )
    return already_dm.scalars().first()
async def check_user_in_dm(db:AsyncSession,current_user_username:str,dm_id:int):
    in_dm = await db.execute(
                        select(Dms).filter(
                            or_(
                                and_(Dms.sender == current_user_username, Dms.id == dm_id),
                                and_(Dms.receiver == current_user_username, Dms.id == dm_id)
                            )
                        )
                    )
    return in_dm.scalars().first()

async def create_new_dm(db:AsyncSession,current_user_username:str,remote_user_username:str):
    dm = Dms(sender=current_user_username, receiver=remote_user_username)
    db.add(dm)
    await db.flush()
    return {"dm_id":dm.id,"receiver":dm.receiver,"sender":dm.sender}

async def get_all_dms(db:AsyncSession,current_user_username:str):
    dms = await db.execute(
                        select(Users.profile, Users.username, Users.status, Dms.id)
                                .join(Dms,
                                      or_(
                                          and_(Dms.receiver == current_user_username,Dms.sender == Users.username),
                                          and_(Dms.sender == current_user_username,Dms.receiver == Users.username)
                                      )
                                    )
                                .filter(Users.username != current_user_username)
                        )
    return dms.all()

async def get_all_dm_information(db:AsyncSession,current_user_username:str,dm_id:int):
    dm_information = await db.execute(
                                select(Users.profile, Users.username, Users.status, Dms.id)
                                    .join(Dms,
                                        and_(
                                            Dms.id == dm_id,
                                            or_(
                                                and_(Dms.receiver == current_user_username, Dms.sender == Users.username),
                                                and_(Dms.sender == current_user_username, Dms.receiver == Users.username)
                                            )
                                        )
                                    )
                                    .filter(Users.username != current_user_username)
                                )
    return dm_information.first()

async def get_all_dm_messages(db:AsyncSession,dm_id:int):
    dm_messages = await db.execute(
                            select(Dm_Messages.dm, Dm_Messages.username, Dm_Messages.link, Dm_Messages.text,
                                   Dm_Messages.file,Dm_Messages.created_date.label("date"), Dm_Messages.filetype,
                                   Dm_Messages.serverinviteid, Server.name.label("servername"),Server.profile.label("serverprofile"),
                                   Users.profile, Users.status)
                                .outerjoin(Server,
                                            Server.id == Dm_Messages.serverinviteid
                                )
                                .join(Users,
                                        Dm_Messages.username == Users.username
                                )
                                .filter(Dm_Messages.dm == dm_id).order_by(Dm_Messages.id)
                            )
    return dm_messages.all()










