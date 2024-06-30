import "./Server.css"
import ServerTopics from "./ServerTopics.js"
import ServerChat from "./ServerChat.js"
import ServerUsers from "./ServerUsers.js"
import InviteUsers from "./InviteUsers.js"
import {useEffect,useState,useContext} from "react"
import {useParams,useNavigate} from "react-router-dom"
import {Context} from "../Context.js"

export default function Server(){
    const {id} = useParams()
    const {showInviteUsers} = useContext(Context)
    const [serverOwner,setServerOwner] = useState("")
    const [serverName,setServerName] = useState("")
    const [serverProfile,setServerProfile] = useState("")
    const navigate = useNavigate()
    const token = localStorage.getItem("token")

    useEffect(() => {
        async function getServerInformation(){
            const url = "/api/server/" + id
            const requestOptions = {
                  method: 'GET',
                  headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
            }
            const response = await fetch(url,requestOptions)
            const data = await response.json()
            if(response.status === 401){
                navigate("/login")
            }
            if(response.status === 403){
                navigate("/")
            }
            else{
                setServerOwner(data.owner)
                setServerName(data.name)
                setServerProfile(data.profile)
            }
        }

        getServerInformation()
    },[id])
    return(
        <div>
            <div className={showInviteUsers ? "discord-server-container create-server-background" :"discord-server-container"}>
                <ServerTopics serverName={serverName}/>
                <ServerChat serverName={serverName}/>
                <ServerUsers serverName={serverName} />
            </div>
            <InviteUsers serverName={serverName} serverProfile={serverProfile}/>
        </div>
    )
}