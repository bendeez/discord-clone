import "./Servers.css"
import {useState,useEffect,useContext} from "react"
import {Context} from "../Context.js"
import {useNavigate} from "react-router-dom"

export default function Servers(){
    const {username,profile,serverWebsocket,changeDmProfile,changeFriendProfile,showCreateServer,changeShowServer,changeServerName,resetServerFile,servers,getServers,showInviteUsers} = useContext(Context)
    const [notifications,setNotifications] = useState([])
    const [messageHover,setMessageHover] = useState("")
    const [serverHover,setServerHover] = useState("")
    const token = localStorage.getItem("token")
    const navigate = useNavigate()
    useEffect(() => {
        async function getNotifications(){
            const url = "/api/notifications"
            const requestOptions = {
                  method: 'GET',
                  headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
            }
            const response = await fetch(url,requestOptions)
            const data = await response.json()
            if(response.status === 401){
                navigate("/login")
            }else{
                setNotifications(data)
            }
        }

        getNotifications()
        getServers()
    },[])
    useEffect(() => {
        function handleMessage(event){
            const message = JSON.parse(event.data)
            if(message.chat === "notification"){
                if(message.type === "message"){
                    setNotifications(Notifications => (
                        Notifications.find(notification => notification.dm === message.dm) ?
                            (Notifications.map(notification => (
                                notification.dm === message.dm ? {...notification,count:notification.count + 1,profile:message.profile} : notification
                            ))
                            ) : (
                                [...Notifications,{...message,count:1}]
                            )
                    ))
                    changeDmProfile(message.sender,message.profile)
                    changeFriendProfile(message.sender,message.profile)
                }
           }
      }
        if(serverWebsocket){
        serverWebsocket.addEventListener("message",handleMessage)
        return (() => {
            serverWebsocket.removeEventListener("message",handleMessage)
        })
        }
    },[serverWebsocket])
    async function deleteNotification(dmId){
        navigate("/dm/" + dmId)
        const url = "/api/notification"
        const requestOptions = {
              method: 'DELETE',
              headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
              body:JSON.stringify({"id":dmId})
        }
        const response = await fetch(url,requestOptions)
        setNotifications(Notifications => (
            Notifications.filter(notification => notification.dm !== dmId)
        ))
    }
    return(
        <div className={showInviteUsers ? "servers-dms create-server-background" : "servers-dms"}>
             <img src="/directmessages.png" onClick={() => navigate("/")}/>
             <div className="servers-dms-container">
                {notifications && (
                    <div className="notifications">
                        {notifications.map((notification,index) => (
                            <div className="notification" onClick={() => deleteNotification(notification.dm)} onMouseOver={() => setMessageHover(index)} onMouseOut={() => setMessageHover("")}>
                                <img src={notification.profile}/>
                                <div className="message-count">{notification.count}</div>
                                {messageHover === index && (
                                    <div className="notification-username">
                                        <p>{notification.sender}</p>
                                    </div>
                                )
                                }
                            </div>
                           )
                           )
                         }
                    </div>
                )
                }
                {servers && (
                    <div className="servers">
                        {servers.map((server,index) => (
                            <div className="server" onClick={() => navigate("/server/" + server.id)} onMouseOver={() => setServerHover(index)} onMouseOut={() => setServerHover("")}>
                                <img src={server.profile}/>
                                {serverHover === index && (
                                    <div className="server-name">
                                        <p>{server.name}</p>
                                    </div>
                                )
                                }
                            </div>
                        ))}
                    </div>
                )}
            </div>
            <div className="add-server" onClick={() => {changeShowServer(); changeServerName(`${username}'s server`); resetServerFile()}}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-plus"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg></div>
        </div>
    )
}