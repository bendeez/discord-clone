import "./InviteUsers.css"
import {useState,useEffect,useContext} from "react"
import {useNavigate,useParams} from "react-router-dom"
import {Context} from "../Context.js"


export default function InviteUsers({serverName,serverProfile}){
    const {id} = useParams()
    const [inviteFriends,setInviteFriends] = useState([])
    const {username,profile,allFriends,getAllFriends,showInviteUsers,changeShowInviteUsers,serverUsers,serverWebsocket} = useContext(Context)
    const token = localStorage.getItem("token")
    const navigate = useNavigate()
    useEffect(() => {
        getAllFriends()
    },[])
    useEffect(() => {
        setInviteFriends(allFriends)
    },[allFriends])
    function filterInviteFriends(event){
        const regex = new RegExp(`^${event.target.value}`,"i")
        setInviteFriends(allFriends.filter(friend => regex.test(friend.username)))
    }
    function inviteUser(dmId,otherUser){
        const date = new Date()
        if(serverWebsocket){
            serverWebsocket.send(JSON.stringify({"chat":"dm","dm":dmId,"type":"link","serverinviteid":id,"username":username,"profile":profile,"otheruser":otherUser,"servername":serverName,"serverprofile":serverProfile,"date":date}))
            changeShowInviteUsers()
            navigate("/dm/" + dmId)
        }
    }
    return(
        <div>
            {showInviteUsers && serverUsers && (
                <div className="invite-users-container">
                    <div className="invite-users-container-top">
                        <p>{`Invite friends to ${serverName}`}</p>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="gray" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-x exit" onClick={changeShowInviteUsers}><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    </div>
                    <input type="text" placeholder="Search for friends" onChange={filterInviteFriends}/>
                    {inviteFriends && (
                        <div className="invite-users">
                            {inviteFriends.filter(friend => serverUsers.every(user => user.username !== friend.username)).map(friend => (
                                <div className="invite-user">
                                    <div className="invite-profile">
                                        <div className="dm-profile">
                                            <img src={friend.profile} />
                                            <div className={friend.status === "online" ? "online" : "offline"}></div>
                                        </div>
                                         <p>{friend.username}</p>
                                     </div>
                                     <button onClick={() => inviteUser(friend.dmid,friend.username)}>Invite</button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
                )
            }
        </div>
    )
}