import "./ServerChat.css"
import {useState,useEffect,useRef,useContext} from "react"
import {useParams,useNavigate} from "react-router-dom"
import {Context} from "../Context.js"

export default function ServerChat({serverName}){
    const {id} = useParams()
    const {username,profile,getServerUsers,serverWebsocket} = useContext(Context)
    const [messages,setMessages] = useState([])
    const navigate = useNavigate()
    const [filePreview,setFilePreview] = useState(null)
    const fileInputRef = useRef(null)
    const textInputRef = useRef(null)
    const messageRef = useRef(null)
    const scrollRef = useRef(null)
    const [autoScroll,setAutoScroll] = useState(true)
    const [messageInput,setMessageInput] = useState("")
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
        async function getMessages(){
            const url = `${process.env.REACT_APP_API_BACKEND}/servermessages/` + id
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
        getMessages()
    },[id])
    useEffect(() => {
        function onMessage(event){
            const message = JSON.parse(event.data)
            if(message.chat === "server" && message.server === parseInt(id)){
                if(message.type === "announcement"){
                    getServerUsers(id)
                }
                if(["text","file","textandfile","announcement"].includes(message.type)){
                    setMessages(Messages => (
                        [...Messages.map(prevmessage => (
                            prevmessage.username === message.username ? {...prevmessage,profile:message.profile} : prevmessage
                        )),message]
                    ))
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
                serverWebsocket.send(JSON.stringify({"chat":"server","server":id,"type":"textandfile","text":messageInput,"file":filePreview.src,"filetype":filePreview.type,"username":username,"profile":profile,"date":date}))
            }else if(messageInput){
                serverWebsocket.send(JSON.stringify({"chat":"server","server":id,"type":"text","text":messageInput,"username":username,"profile":profile,"date":date}))
            }else if(filePreview){
                serverWebsocket.send(JSON.stringify({"chat":"server","server":id,"type":"file","file":filePreview.src,"filetype":filePreview.type,"username":username,"profile":profile,"date":date}))
            }
            setFilePreview(null)
            setMessageInput("")
            fileInputRef.current.value = ""
            setAutoScroll(true)
        }
    }
    return(
        <div className="server-chat">
            <div className="server-chat-header">
                <p>{serverName}</p>
            </div>
            <div className="dm-conversation" style={filePreview ? {height:"38rem"} : {}} ref={scrollRef} onScroll={handleScroll}>
                <div className="dm-conversation-beginning">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-hash"><line x1="4" y1="9" x2="20" y2="9"></line><line x1="4" y1="15" x2="20" y2="15"></line><line x1="10" y1="3" x2="8" y2="21"></line><line x1="16" y1="3" x2="14" y2="21"></line></svg>
                    <p>Welcome to {serverName}</p>
                    <span>This is the start of the #general channel</span>
                </div>
                <div className="dm-conversation-body" id="dm-conversation-body">
                    {messages && messages.length > 0 && (
                        messages.map(message => (
                            <div>
                                {message.announcement ? (
                                <div className="join-announcement">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="green" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-right"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                                    <p>{message.announcement}</p>
                                    <p className="dm-message-date">{turnDateToString(message.date)}</p>
                                </div>
                                ) : (
                                    <div className="dm-message">
                                        <img src={message.profile} className="dm-message-profile-image"/>
                                        <div className="dm-message-body">
                                            <div className="dm-message-body-top">
                                                <span>{message.username}</span>
                                                <p className="dm-message-date">{turnDateToString(message.date)}</p>
                                            </div>
                                            {message.text && <p>{message.text}</p>}
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
                                )
                               }
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
               <input type="text" name="message" className="message-input" autofocus placeholder={`Message ${serverName}`} value={messageInput} ref={textInputRef} onChange={(e) => setMessageInput(e.target.value)}/>
           </form>
    </div>
    )
}