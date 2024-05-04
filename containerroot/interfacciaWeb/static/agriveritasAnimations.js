const chatContainer = document.getElementById("dialoguePart")
const chatHistory = document.getElementById("chat-history")

const sendBut = document.getElementById("send-button")
const queryInput = document.getElementById("user-input")


const IA_class = "userA"
const Uman_class = "userQ"


sendBut.addEventListener("click", () => {
    invokeQueryAnswer()
})

function invokeQueryAnswer(){
    
    //input
    const textToSend = queryInput.value;
    appendMessage(textToSend, Uman_class, chatHistory)
    
    //elaborate
    const response = computeReponse(textToSend)

    //output //gestito in computeResponse
    //appendMessage(response, IA_class, chatHistory)

}

//in realtà where non è utilizzato
function manageIAResponse(text, where, messageElement){
    let index = 0;
    let words = text.split(" ")
    

    const intervalId = setInterval(() => {
        if (index < words.length){
            messageElement.innerHTML += words[index] + " ";
            index++;
            chatContainer.scrollTop = chatContainer.scrollHeight;
        } else {
            clearInterval(intervalId);
            queryInput.value = ""
        }

        // if (index < text.length) {
        //     for (let a = 0; a < 5; a++) {
        //         messageElement.innerHTML += text.charAt(index);
        //         index++;
        //     }
        // } else {
        //     clearInterval(intervalId);
        // }
    }, 100); 
}

function startIAResponse(text, where) {
    const newMessage = document.createElement("p");
    manageIAResponse(text, where, newMessage); //in realtà where non è utilizzato
    return newMessage;
}

function appendMessage(text, user, where) {
    const newMessagge = document.createElement("li")
    newMessagge.classList.add(user)
    const divContainerP = document.createElement("div")
    divContainerP.classList.add("card")
    // const message = document.createElement("p")
    let message;
    if (user == IA_class){
        message = startIAResponse(text, where)
    } else {
        message = document.createElement("p")
        message.innerHTML = text
    }

    divContainerP.appendChild(message)
    newMessagge.appendChild(divContainerP)
    where.appendChild(newMessagge)
}

queryInput.addEventListener("keydown", (event) => {
    if ((event.key === "Enter" || event.keyCode === 13) && event.shiftKey) {
      event.preventDefault(); // prevent new line insertion
      // send the text
      const text = queryInput.value.trim();
      if (text) {
        // your logic to send the text
        console.log("Sending text:", text);
        // clear the textarea
        invokeQueryAnswer()
      }
    }
  });

function getBasicURL() {
    ip="http://137.204.107.40"
    port="37336"
    return ip + ":" + port
}

function computeReponse(queryText){
    query="IAresponse"
    // Create an XMLHttpRequest object
    const xhttp = new XMLHttpRequest();

    // Define a callback function
    xhttp.onload = function() {
        // Here you can use the Data
        console.log(xhttp.responseText)
        let jsonR = JSON.parse(xhttp.responseText)
        if (jsonR.status == 0 || jsonR.status == 1){
            appendMessage(jsonR.message, IA_class, chatHistory)
        } else {
            appendMessage("ERRORE: RICARICARE LA PAGINA", IA_class, chatHistory)
        }
    }

    // console.log("-> " +ip)
    let urlTmp = getBasicURL()+"/"+query+"/"
    if (actRegCode != ""){
        urlTmp += actRegCode +"?qt="+queryText
    }   
    console.log(urlTmp)
    // Send a request
    xhttp.open("GET", urlTmp);
    xhttp.send();
    // return "Sono ancora una piccola versione puramente di prototipazione, non riesco ancora a soddisfare alcuna richiesta. Torna presto per delle novità!"
}

















//////////////////////////////////////////////


const whereAddRegion = document.getElementById("selecRegion")
const regions = ["Emilia-Romagna"] //["Veneto", "Emilia-Romagna", "Puglia"]
const regionTextLinks = ["Agrea"] //["Avepa", "Agrea", "PSR"]
const regionLinkLinks = ["#"] //["https://www.avepa.it", "#", "#"]
const regionCode = ["ER"] //["V", "ER", "P"]
let actRegSelected = -1
let actRegCode = "noRegionSelected"

function refreshButtons(){
    for (let indexRegionConsidered = 0; indexRegionConsidered < regions.length; indexRegionConsidered++) {
        let tmpDiv = document.createElement("div")
        tmpDiv.classList.add("card")
        tmpDiv.classList.add("region")

        let tmpButton = document.createElement("button")
        tmpButton.disabled = (indexRegionConsidered == actRegSelected)
        tmpButton.addEventListener("click", () => {
            actRegSelected = indexRegionConsidered
            whereAddRegion.innerHTML = ""
            console.log("Selected: " + regionCode[indexRegionConsidered])
            actRegCode = regionCode[indexRegionConsidered]
            chatHistory.innerHTML = ""
            refreshButtons()
        })

        let lll = document.createElement("a")
        lll.href = regionLinkLinks[indexRegionConsidered]
        lll.innerHTML = regionTextLinks[indexRegionConsidered]

        tmpButton.innerHTML = "Regione " + regions[indexRegionConsidered] + " - "
        tmpButton.appendChild(lll)

        tmpDiv.appendChild(tmpButton)

        whereAddRegion.appendChild(tmpDiv)
        
    }
    
}
refreshButtons()

// {/* <div class="card region">
//                 <button>Regione Veneto - <a href="https://www.avepa.it/">Avepa</a></button>
//             </div> */}






const lastUpdateDateSpan = document.getElementById("last-update-date")

// Create an XMLHttpRequest object
const xhttp = new XMLHttpRequest()

// Define a callback function
xhttp.onload = function() {
    console.log(xhttp.responseText)
    const responseForPopulatePage = JSON.parse(xhttp.responseText)
    lastUpdateDateSpan.innerHTML = responseForPopulatePage.last_update_date
}

// Send a request
xhttp.open("GET", getBasicURL() + "/initInfo");
xhttp.send();
// return "Sono ancora una piccola versione puramente di prototipazione, non riesco ancora a soddisfare alcuna richiesta. Torna presto per delle novità!"
