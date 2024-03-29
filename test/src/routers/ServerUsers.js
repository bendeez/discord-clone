import "./ServerUsers.css"
import {useState,useEffect,useContext} from "react"
import {useParams,useNavigate} from "react-router-dom"
import {Context} from "../Context.js"

export default function ServerUsers({serverName}){
    const {id} = useParams()
    const {showInviteUsers,changeShowInviteUsers,serverUsers,getServerUsers,serverWebsocket,updateServerUsersStatus} = useContext(Context)
    const navigate = useNavigate()
    const token = localStorage.getItem("token")
    useEffect(() => {
        getServerUsers(id)
    },[id])
    useEffect(() => {
        function onMessage(event){
            const message = JSON.parse(event.data)
            if(message.chat === "notificationall"){
                if(message.type === "status"){
                    updateServerUsersStatus(message.username,message.status)
                }
            }
        }
        if(serverWebsocket){
            serverWebsocket.addEventListener("message",onMessage)
            return () => {
                serverWebsocket.removeEventListener("message",onMessage)
            }
        }
    },[serverWebsocket,id])
    return(
        <div className="server-users">
        {serverUsers && serverUsers.length > 0 && (
            <div>
            {serverUsers.filter(user => user.status == "online").length > 0 && (
                <div className="server-users-container">
                    <p className="server-role">Online - {serverUsers.filter(user => user.status == "online").length}</p>
                    <div className="server-users-list-online">
                         {serverUsers.filter(user => user.status == "online").map(user => (
                            <div className="server-user">
                                <div className="server-user-profile">
                                    <img src={user.profile}/>
                                    <div className="online"></div>
                                </div>
                                <p>{user.username}</p>
                            </div>
                          ))}
                    </div>
                </div>
            )}
            {serverUsers.filter(user => user.status == "offline").length > 0 && (
                <div className="server-users-container">
                    <p className="server-role">Offline - {serverUsers.filter(user => user.status == "offline").length}</p>
                    <div className="server-users-list-offline">
                         {serverUsers.filter(user => user.status == "offline").map(user => (
                            <div className="server-user">
                                <div className="server-user-profile">
                                    <img src={user.profile}/>
                                    <div className="offline"></div>
                                </div>
                                <p>{user.username}</p>
                            </div>
                          ))}
                    </div>
                </div>
            )}
                {!showInviteUsers && (
                <p className="show-invite-list" onClick={changeShowInviteUsers}>Invite People</p>
                )
                }
            </div>
        )}
        </div>
    )
}