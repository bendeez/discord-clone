import "./Home.css"
import Servers from "./Servers.js"
import Dms from "./Dms.js"
import ActiveNow from "./ActiveNow.js"
import CreateServer from "./CreateServer.js"
import {useState,useEffect,useContext} from "react"
import {useNavigate,Outlet,useLocation} from "react-router-dom"
import {Context} from "../Context.js"

export default function Home(){
    const navigate = useNavigate()
    const location = useLocation()
    const token = localStorage.getItem("token")
    const {getUserInformation,username,profile,changeServerWebsocket,showCreateServer} = useContext(Context)

    useEffect(() => {
        getUserInformation()
    },[])

    useEffect(() => {
        if(username){
            const websocket = new WebSocket(`ws://127.0.0.1:3000/ws/server/${token}`)
            websocket.onopen = () => {
                websocket.send(JSON.stringify({"chat":"notificationall","type":"status","status":"online","username":username}))
                window.addEventListener("unload",function () {
                    websocket.send(JSON.stringify({"chat":"notificationall","type":"status","status":"offline","username":username}))
                })
            }
            changeServerWebsocket(websocket)
            return () => {
                websocket.close()
            }
        }
    },[username])

    return(
        <div>
            {username && profile && (
                <div>
                    <div className={showCreateServer ? "discord-container create-server-background" : "discord-container"}>
                        <Servers/>
                        {location.pathname.startsWith("/server") ? (
                            <Outlet/>
                        ) : (
                            <div className="discord-dm-container">
                                <Dms/>
                                <Outlet/>
                                <ActiveNow/>
                            </div>
                        )}
                    </div>
                    {showCreateServer && (
                        <CreateServer/>
                    )}
                </div>
            )}
        </div>
    )
}