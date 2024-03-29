import "./Register.css"
import {useNavigate} from "react-router-dom"
import {useState} from "react"

export default function Login(){
    const navigate = useNavigate()
    const [registerData,setRegisterData] = useState({email:"",username:"",password:""})
    const [error,setError] = useState("")
    function registerChange(event){
        const {name,value} = event.target
        setRegisterData(RegisterData => (
            {...RegisterData,[name]:value}
        ))
    }
    async function registerSubmit(event){
        event.preventDefault()
        const url = "/api/user"
        const requestOptions = {
              method: 'POST',
              headers:{'Content-Type': 'application/json'},
              body:JSON.stringify({"email":registerData.email,"username":registerData.username,"password":registerData.password})
        }
        const response = await fetch(url,requestOptions)
        const data = await response.json()
        if(response.status === 409){
            setError(data.detail)
        }else{
            navigate("/login")
        }
    }
    return(
        <div>
            <img className="register-background" src="loginbackground.png"/>
            <div className="register-container">
                <div className="register">
                    <h2>Create an account</h2>
                    {error && (
                        <p className="error">{error}</p>
                    )}
                    <form className="register-form" id="register-form" onSubmit={registerSubmit}>
                        <label for="email">EMAIL *</label>
                        <input type="text" name="email" onChange={registerChange} required/>
                        <label for="username">USERNAME *</label>
                        <input type="text" name="username" onChange={registerChange} required/>
                        <label for="password">PASSWORD *</label>
                        <input type="password" name="password" onChange={registerChange} required/>
                        <button>Continue</button>
                    </form>
            </div>
      </div>
        </div>
    )
}

