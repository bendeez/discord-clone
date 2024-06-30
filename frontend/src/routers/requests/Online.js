import {useEffect,useState,useContext} from "react"
import {Context} from "../../Context.js"
import {useNavigate} from "react-router-dom"

export default function Online(){
    const token = localStorage.getItem("token")
    const [onlineFriends,setOnlineFriends] = useState([])
    const {serverWebsocket,allFriends,getAllFriends,changeFriendStatus,deleteFriend} = useContext(Context)
    const navigate = useNavigate()
    useEffect(() => {
        getAllFriends()
    },[])
    useEffect(() => {
        if(allFriends){
            setOnlineFriends(allFriends.filter(friend => friend.status === "online"))
        }
    },[allFriends])
    useEffect(() => {
        function onMessage(event){
            const message = JSON.parse(event.data)
            if(message.chat === "notificationall"){
                if(message.type === "status"){
                    changeFriendStatus(message.username,message.status)
                }
            }
        }
        if(serverWebsocket){
            serverWebsocket.addEventListener("message",onMessage)
            return () => {
                serverWebsocket.removeEventListener("message",onMessage)
            }
        }
    },[serverWebsocket])
    function filterOnlineFriends(event){
        const regex = new RegExp(`^${event.target.value}`,"i")
        setOnlineFriends(allFriends.filter(friend => regex.test(friend.username) && friend.status === "online"))
    }
    return(
        <div className="user-requests-container">
            <form onSubmit={(e) => e.preventDefault()}>
                <input type="text" placeholder="Search" onChange={filterOnlineFriends}/>
            </form>
            <p className="count">ONLINE - <span id="friends-count">{onlineFriends && onlineFriends.length}</span></p>
            <div className="pending-requests">
                {allFriends && allFriends.length > 0 && (
                    onlineFriends.map(friend => (
                        <div className="request" onClick={() => navigate("/dm/" + friend.dmid)}>
                                <div className="dm-profile">
                                    <img src={friend.profile}/>
                                    <div className={friend.status === "online" ? "online" : "offline"}></div>
                                </div>
                                 <p>{friend.username}</p>
                                 <div className="request-icons">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-x remove" onClick={(event) => deleteFriend(event,friend.username)}><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                                </div>
                         </div>

                    )
                    )
                )}
            </div>
        </div>
    )
}