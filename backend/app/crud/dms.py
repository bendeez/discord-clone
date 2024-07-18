from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, union, case, func, or_, and_
from sqlalchemy.orm import selectinload
from app.schemas.websocket_data.notification_message import NotificationNewDm
from app.models.dms import Dms, Dm_Messages
from app.models.servers import Server
from app.models.user import Users
from app.ConnectionManagers.ServerConnectionManager import server_manager



async def check_already_created_dm(db: AsyncSession, current_user: Users, remote_user_username: str):
    dm = await get_dm(db=db, current_user=current_user, remote_user_username=remote_user_username)
    if dm is not None:
        return True
    return False

async def get_dm(db: AsyncSession, current_user: Users, remote_user_username):
    dm = await db.execute(
        select(Dms).filter(
            or_(
                and_(Dms.sender == current_user.username, Dms.receiver == remote_user_username),
                and_(Dms.receiver == current_user.username, Dms.sender == remote_user_username)
            )
        )
    )
    return dm.scalars().first()

async def check_user_in_dm(db: AsyncSession, current_user: Users, dm_id: int):
    dm = await db.execute(select(Dms)
                                .where(Dms.id == dm_id)
                                .options(selectinload(Dms.sender_user),
                                         selectinload(Dms.receiver_user)))
    dm = dm.scalars().first()
    if dm is not None:
        if current_user in [dm.sender_user,dm.receiver_user]:
            return True
    return False


async def create_new_dm(db: AsyncSession, current_user: Users, remote_user_username: str):
    from app.crud.friends import get_friend
    dm = Dms(sender=current_user.username, receiver=remote_user_username)
    friend = await get_friend(db=db,current_user=current_user,remote_user_username=remote_user_username)
    if friend is not None:
        friend.dm = dm
    else:
        db.add(dm)
    await db.commit()
    await db.refresh(dm)
    return dm


async def get_all_dms(db: AsyncSession, current_user: Users):
    received_dms = (select(Dms.id, Users.username,
                           Users.profile, Users.status)
                    .join_from(Dms, Dms.sender_user)
                    .where(Dms.receiver == current_user.username))
    sent_dms = (select(Dms.id, Users.username,
                       Users.profile, Users.status)
                .join_from(Dms, Dms.receiver_user)
                .where(Dms.sender == current_user.username))
    dms = await db.execute(union(received_dms, sent_dms))
    return dms.all()


async def get_all_dm_information(db: AsyncSession, current_user: Users, dm_id: int):
    dm_user = await db.execute(select(
                                case(
                                    (Dms.sender == current_user.username,
                                     (select(
                                            func.row(
                                                Users.username,
                                                Users.profile,
                                                Users.status,
                                                Dms.id)
                                     ).where(Users.username == Dms.receiver)).scalar_subquery()
                                     ),
                                    (Dms.receiver == current_user.username,
                                     (select(
                                         func.row(
                                             Users.username,
                                             Users.profile,
                                             Users.status,
                                             Dms.id)
                                     ).where(Users.username == Dms.sender)).scalar_subquery()
                                     )
                                ).label("information")
                                )
                              .where(Dms.id == dm_id))
    return dm_user.first()


async def get_all_dm_messages(db: AsyncSession, dm_id: int):
    dm_messages = await db.execute(select(Dm_Messages.dm, Dm_Messages.link,
                                          Dm_Messages.text, Dm_Messages.file,
                                          Dm_Messages.filetype, Dm_Messages.serverinviteid,
                                          Dm_Messages.date,
                                          Users.username, Users.profile, Users.status,
                                          Server.name.label("servername"),
                                          Server.profile.label("serverprofile"))
                                   .join_from(Dm_Messages, Dm_Messages.user)
                                   .outerjoin_from(Dm_Messages, Dm_Messages.server_invite_info)
                                   .where(Dm_Messages.dm == dm_id)
                                   .order_by(Dm_Messages.id))
    return dm_messages.all()

async def delete_current_dm(db: AsyncSession, dm: Dms):
    await db.delete(dm)
    await db.commit()

async def delete_current_dm_message(db: AsyncSession, dm_message: Dm_Messages):
    await db.delete(dm_message)
    await db.commit()

async def send_new_dm_notification(current_user: Users, dm: Dms):
    """
        add the dm id to the users' dm_ids list so they can
        send messages in that dm
    """
    server_manager.add_valid_server_or_dm(usernames=[dm.sender, dm.receiver], type="dm_ids", id=dm.id)
    create_dm_notification = NotificationNewDm(**{"sender": dm.sender, "receiver": dm.receiver})
    await server_manager.broadcast_from_route(sender_username=current_user.username, message=create_dm_notification)