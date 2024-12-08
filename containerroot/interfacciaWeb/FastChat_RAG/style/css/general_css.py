block_css = """
#notice_markdown .prose {
    font-size: 110% !important;
}
#notice_markdown th {
    display: none;
}
#notice_markdown td {
    padding-top: 6px;
    padding-bottom: 6px;
}
#arena_leaderboard_dataframe table {
    font-size: 110%;
}
#full_leaderboard_dataframe table {
    font-size: 110%;
}
#model_description_markdown {
    font-size: 110% !important;
}
#leaderboard_markdown .prose {
    font-size: 110% !important;
}
#leaderboard_markdown td {
    padding-top: 6px;
    padding-bottom: 6px;
}
#leaderboard_dataframe td {
    line-height: 0.1em;
}
#about_markdown .prose {
    font-size: 110% !important;
}
#ack_markdown .prose {
    font-size: 110% !important;
}
#chatbot .prose {
    font-size: 105% !important;
}
.sponsor-image-about img {
    margin: 0 20px;
    margin-top: 20px;
    height: 40px;
    max-height: 100%;
    width: auto;
    float: left;
}

.chatbot h1, h2, h3 {
    margin-top: 8px; /* Adjust the value as needed */
    margin-bottom: 0px; /* Adjust the value as needed */
    padding-bottom: 0px;
}

.chatbot h1 {
    font-size: 130%;
}
.chatbot h2 {
    font-size: 120%;
}
.chatbot h3 {
    font-size: 110%;
}
.chatbot p:not(:first-child) {
    margin-top: 8px;
}

.typing {
    display: inline-block;
}

.cursor {
    display: inline-block;
    width: 7px;
    height: 1em;
    background-color: black;
    vertical-align: middle;
    animation: blink 1s infinite;
}

.dark .cursor {
    display: inline-block;
    width: 7px;
    height: 1em;
    background-color: white;
    vertical-align: middle;
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    50.1%, 100% { opacity: 0; }
}

.app {
  max-width: 100% !important;
  padding: 20px !important;               
}

a {
    color: yellow; /*#1976D2;  Your current link color, a shade of blue */
    text-decoration: none; /* Removes underline from links */
}
a:hover {
    color: black; /*#63A4FF;  This can be any color you choose for hover */
    text-decoration: underline; /* Adds underline on hover */
}

p .reported-text{
    color: black;    
}

span{
    color: black;
}
"""