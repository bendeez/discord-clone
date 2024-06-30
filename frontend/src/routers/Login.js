import "./Login.css"
import {useNavigate} from "react-router-dom"
import {useState} from "react"

export default function Login(){
    const navigate = useNavigate()
    const [loginData,setLoginData] = useState({username:"",password:""})
    const [error,setError] = useState("")
    function loginChange(event){
        const {name,value} = event.target
        setLoginData(LoginData => (
            {...LoginData,[name]:value}
        ))
    }
    async function loginSubmit(event){
        event.preventDefault()
        const url = "/api/login"
        const requestOptions = {
              method: 'POST',
              headers:{'Content-Type': 'application/json'},
              body:JSON.stringify({"username":loginData.username,"password":loginData.password})
        }
        const response = await fetch(url,requestOptions)
        const data = await response.json()
        if(response.status === 401){
            setError(data.detail)
        }else{
            localStorage.setItem("token",data.access_token)
            navigate("/")
        }
    }
    return(
        <div>
            <img className="login-background" src="loginbackground.png"/>
            <div className="login-container">
                <div className="login">
                    <h2>Welcome back!</h2>
                    <p>We're so exited to see you again!</p>
                    {error && (
                        <p className="error">{error}</p>
                    )}
                    <form className="login-form" onSubmit={loginSubmit}>
                        <label for="username">USERNAME *</label>
                        <input type="text" name="username" value={loginData.username} onChange={loginChange} required/>
                        <label for="password">PASSWORD *</label>
                        <input type="password" name="password" value={loginData.password} onChange={loginChange} required/>
                        <p className="forgot-password">Forgot your password?</p>
                        <button>Log In</button>
                        <p className="new-account">Need an account? <span className="register-link" onClick={() => navigate("/register")}>Register</span></p>
                    </form>
                </div>
            </div>
        </div>
    )
}