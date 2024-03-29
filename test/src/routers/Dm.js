import "./Dm.css"
import {useParams,useNavigate} from "react-router-dom"
import {useEffect,useState,useContext,useRef} from "react"
import {Context} from "../Context.js"


export default function Dm(){
    const {id} = useParams()
    const [dmUsername,setDmUsername] = useState("")
    const [dmStatus,setDmStatus] = useState("")
    const [dmProfile,setDmProfile] = useState("")
    const [filePreview,setFilePreview] = useState(null)
    const [messages,setMessages] = useState([])
    const fileInputRef = useRef(null)
    const textInputRef = useRef(null)
    const messageRef = useRef(null)
    const scrollRef = useRef(null)
    const [autoScroll,setAutoScroll] = useState(true)
    const [messageInput,setMessageInput] = useState("")
    const {username,profile,serverWebsocket,getServers} = useContext(Context)
    const navigate = useNavigate()
    const token = localStorage.getItem("token")
    function scrollToBottom(){
        if(messageRef.current && autoScroll){
            messageRef.current.scrollIntoView()
        }
    }
    useEffect(() => {
        scrollToBottom()
    },[messages])
    useEffect(() => {
        async function getDmInformation(){
            const url = "/api/dm/" + id
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
                setDmUsername(data.username)
                setDmProfile(data.profile)
                setDmStatus(data.status)
            }
        }
        async function getMessages(){
            const url = "/api/dmmessages/" + id
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
                setMessages(data)
            }
        }
        getDmInformation()
        getMessages()
    },[id])
    useEffect(() => {
        function onMessage(event){
            const message = JSON.parse(event.data)
            if(message.chat === "notificationall"){
                if(message.type === "status" && message.username === dmUsername){
                    setDmStatus(message.status)
                }
            }
            if(message.chat === "dm" && message.dm === parseInt(id)){
                setMessages(Messages => (
                [...Messages.map(prevmessage => (
                    prevmessage.username === message.username ? {...prevmessage,profile:message.profile} : prevmessage
                )),message]
                ))
                if(message.username !== username){
                    setDmProfile(message.profile)
                }
            }
        }
        if(serverWebsocket){
            serverWebsocket.addEventListener("message",onMessage)
            return () => {
                serverWebsocket.removeEventListener("message",onMessage)
            }
        }
    },[serverWebsocket,id,dmUsername])
    function turnDateToString (createdDate){
        let date = new Date(createdDate)
        let minutes = date.getMinutes() < 10 ? "0" + date.getMinutes() : date.getMinutes()
        let hours = date.getHours()
        let timeOfDay
        if(hours > 12){
            if(hours - 12 < 10){
                hours = "0" + hours - 12
            }else{
                hours = hours - 12
            }
            timeOfDay = "pm"
        }else{
            if(hours < 10){
                hours = "0" + hours
            }
            timeOfDay = "am"
        }
        let month = date.getMonth() + 1 < 10 ? "0" + (date.getMonth() + 1) : date.getMonth() + 1
        let day = date.getDate() < 10 ? "0" + date.getDate() : date.getDate()
        let year = date.getFullYear()
        let fullDate = `${month}/${day}/${year} ${hours}:${minutes} ${timeOfDay}`
        return fullDate
    }
    function handleScroll(){
        if(scrollRef.current){
            const container = scrollRef.current
            const isScrolledDown = Math.abs(container.scrollTop - (container.scrollHeight - container.clientHeight)) < 1
            setAutoScroll(isScrolledDown)
        }
    }
    function messageFileChange(event){
        const file = event.target.files[0]
        const reader = new FileReader()
        reader.onload = () => {
            const fileInput = reader.result
            const fileSplit = file.name.split(".")
            const fileType = fileSplit[fileSplit.length - 1]
            setFilePreview({type:fileType,src:fileInput})
            if(textInputRef.current){
                textInputRef.current.focus()
            }
        }
        reader.readAsDataURL(file)
    }
    function deletePreviewFile(){
        setFilePreview(null)
        if(fileInputRef.current){
            fileInputRef.current.value = ""
        }
    }
    function sendMessage(event){
        event.preventDefault()
        const date = new Date()
        if(serverWebsocket){
            if(messageInput && filePreview){
                serverWebsocket.send(JSON.stringify({"chat":"dm","dm":id,"type":"textandfile","text":messageInput,"file":filePreview.src,"filetype":filePreview.type,"otheruser":dmUsername,"username":username,"profile":profile,"date":date}))
            }else if(messageInput){
                serverWebsocket.send(JSON.stringify({"chat":"dm","dm":id,"type":"text","text":messageInput,"otheruser":dmUsername,"username":username,"profile":profile,"date":date}))
            }else if(filePreview){
                serverWebsocket.send(JSON.stringify({"chat":"dm","dm":id,"type":"file","file":filePreview.src,"filetype":filePreview.type,"otheruser":dmUsername,"username":username,"profile":profile,"date":date}))
            }
            setFilePreview(null)
            setMessageInput("")
            fileInputRef.current.value = ""
            setAutoScroll(true)
        }
    }
    async function joinServer(link){
        const url = "/api/server/user"
        const requestOptions = {
              method: 'POST',
              headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
              body:JSON.stringify({"link":link})
        }
        const response = await fetch(url,requestOptions)
        const data = await response.json()
        if(response.status !== 403 && response.status !== 409){
            navigate("/server/" + data.serverid)
            getServers()
        }
    }
    return(
            <div className="dm">
                {dmUsername && dmProfile && dmStatus && (
                    <div>
                        <div className="dm-header-container">
                            <div className="dm-header">
                                <div className="dm-profile">
                                    <img src={dmProfile}/>
                                    <div className={dmStatus === "online" ? "online" : "offline"}></div>
                                </div>
                                <p>{dmUsername}</p>
                            </div>
                            <div className="call" id="call"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-phone-call"><path d="M15.05 5A5 5 0 0 1 19 8.95M15.05 1A9 9 0 0 1 23 8.94m-1 7.98v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg></div>
                        </div>
                        <div className="dm-conversation" style={filePreview ? {height:"38rem"} : {}} ref={scrollRef} onScroll={handleScroll}>
                            <div className="dm-conversation-beginning">
                                <img src={dmProfile}/>
                                <p>{dmUsername}</p>
                                <span>This is the beginning of your direct message history with <span className="dm-conversation-beginning-username">{dmUsername}</span></span>
                            </div>
                            <div className="dm-conversation-body" id="dm-conversation-body">
                                {messages && messages.length > 0 && (
                                    messages.map(message => (
                                        <div className="dm-message">
                                            <img src={message.profile} className="dm-message-profile-image"/>
                                            <div className="dm-message-body">
                                                <div className="dm-message-body-top">
                                                    <span>{message.username}</span>
                                                    <p className="dm-message-date">{turnDateToString(message.date)}</p>
                                                </div>
                                                {message.text && <p>{message.text}</p>}
                                                {message.link && (
                                                    <div>
                                                        <p className="invite-link" onClick={() => joinServer(message.link)}>{message.link}</p>
                                                        <div className="server-invite-container">
                                                            <span>YOU'VE BEEN INVITED TO JOIN A SERVER</span>
                                                            <div className="server-invite">
                                                                <img src={message.serverprofile} />
                                                                <p>{message.servername}</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                )
                                                }
                                                {message.file && (
                                                    message.filetype === "mp4" ?
                                                         (<video controls className="dm-message-video" onLoadedData={scrollToBottom}>
                                                            <source src={message.file} />
                                                          </video>)
                                                         : (<img src={message.file} className="dm-message-image" onLoad={scrollToBottom}/>)
                                                  )
                                                  }
                                            </div>
                                        </div>
                                ))
                                )
                                }
                                <div ref={messageRef}></div>
                            </div>
                   </div>
                    {filePreview && (
                        <div className="file-preview">
                            {filePreview.type === "mp4" ? (
                               <video className="file-preview-file">
                                    <source src={filePreview.src} />
                               </video>
                             ) : (
                                <div>
                               <img className="file-preview-file" src={filePreview.src}/>
                               </div>
                             )
                             }

                            <div className="remove-file" id="remove-file" onClick={deletePreviewFile}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="red" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-trash-2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg></div>
                        </div>
                    )}
                   <form className="send-message" onSubmit={sendMessage}>
                       <label for="file-input" className="file-label"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-plus-circle"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line></svg></label>
                       <input type="file" name="file" id="file-input" className="file-input" ref={fileInputRef} onChange={messageFileChange}/>
                       <input type="text" name="message" className="message-input" autofocus placeholder={`Message @${dmUsername}`} value={messageInput} ref={textInputRef} onChange={(e) => setMessageInput(e.target.value)}/>
                   </form>
               </div>
               )}
           </div>
        )
}