import "./Dms.css"
import {useState,useEffect,useContext} from "react"
import {Context} from "../Context.js"
import {useNavigate} from "react-router-dom"
import UserBox from "./UserBox.js"

export default function Dms(){
    const {dms,getDms,username,profile,serverWebsocket,changeDmStatus} = useContext(Context)
    const token = localStorage.getItem("token")
    const navigate = useNavigate()
    useEffect(() => {
        getDms()
    },[])
    useEffect(() => {
        function onMessage(event){
            const message = JSON.parse(event.data)
            if(message.chat === "notificationall"){
                if(message.type === "status"){
                    changeDmStatus(message.username,message.status)
                }
            }
            if(message.type === "newdm"){
                getDms()
            }
        }
        if(serverWebsocket){
            serverWebsocket.addEventListener("message",onMessage)
            return () => {
                serverWebsocket.removeEventListener("message",onMessage)
            }
        }
    },[serverWebsocket])
    return(
        <div className="dms">
            <div className="find-a-conversation-container">
                <div className="find-a-conversation">
                    Find or start a conversation
                </div>
            </div>
            <div className="dms-nav" id="dms-nav">
                <p id="friends" onClick={() => navigate("/")}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-user"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>Friends</p>
                <p id="nitro"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-gift"><polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>Nitro</p>
                <p id="message-requests"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" classNameName="feather feather-mail"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>Message Requests</p>
                <p id="shop"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-shopping-bag"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>Shop</p>
            </div>
            <p className="direct-messages" id="direct-messages">DIRECT MESSAGES</p>
            <div className="dm-users">
                {dms && dms.length > 0 && (
                    dms.map(dm => (
                        <div className="dm-user" onClick={() => navigate("/dm/" + dm.id)}>
                            <div className="dm-profile">
                                <img src={dm.profile}/>
                                <div className={dm.status === "online" ? "online" : "offline"}></div>
                            </div>
                             <p>{dm.username}</p>
                       </div>
                    ))
                )}
            </div>
            <UserBox/>
        </div>
    )
}