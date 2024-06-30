import "./ServerTopics.css"
import UserBox from "./UserBox.js"
import {useParams} from "react-router-dom"

export default function ServerTopics({serverName}){
    const {id} = useParams()

    return(
        <div className="server-topics">
            <div className="server-title">
                <p>{serverName}</p>
            </div>
            <div className="server-channels">
                <p># general</p>
            </div>
            <UserBox/>
        </div>
    )
}