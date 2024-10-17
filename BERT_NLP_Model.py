# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 21:01:42 2024

@author: RowanBarua
"""

from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
import streamlit as st
import fitz
from torch.nn.functional import softmax

# Load fine-tuned model for question answering
tokenizer = AutoTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
model = AutoModelForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")

# Example bid context and question
context = """
Alan Shearer CBE DL (born 13 August 1970) is an English football pundit and former professional player who played as a striker. Widely regarded as one of the best strikers of all time and one of the greatest players in Premier League history, he is the league's record goalscorer with 260 goals.[notes 1] He was named Football Writers' Association Player of the Year in 1994 and won the PFA Player of the Year award in 1995. In 1996 he came third in both Ballon d'Or and FIFA World Player of the Year awards. In 2004 he was named by Pelé in the FIFA 100 list of the world's greatest living players.[2] Shearer was one of the first two players inducted into the Premier League Hall of Fame in 2021.[3]
Shearer played his entire career in the top level of English football. He started his career at Southampton in 1988 before moving to Blackburn Rovers in 1992, where he established himself as among the most prolific goalscorers in Europe and won the 1994–95 Premier League. In the summer of 1996, he joined his hometown club Newcastle United for a then world record £15 million, and in his first season won his third consecutive Premier League Golden Boot. He played in the 1998 FA Cup and 1999 FA Cup finals, captaining the team in the latter, and eventually became the club's all-time top scorer.[notes 1] He retired at the end of the 2005–06 season.
For the England national team, Shearer appeared 63 times and scored 30 goals.[4] UEFA Euro 1996 was his biggest success at international football; England reached the semi-finals and Shearer was awarded the UEFA Euro Golden Boot and was named in the UEFA Euro Team of the Tournament. He went on to captain England at 1998 FIFA World Cup and UEFA Euro 2000, then retired from international football.
Since retiring as a player in 2006, Shearer has worked as a television pundit for the BBC. In 2009, he briefly left his BBC role to become Newcastle United's manager in the last eight games of their 2008–09 season, in an unsuccessful attempt to save them from relegation. Shearer is a Commander of the Order of the British Empire (CBE), a Deputy Lieutenant of Northumberland, a Freeman of Newcastle upon Tyne and an honorary Doctor of Civil Law of Northumbria and Newcastle Universities.
Early life
Shearer was in the Gosforth area of Newcastle upon Tyne,[5] the son of Anne and sheet-metal worker Alan Shearer. His parents were working class. His father encouraged him to play football in his youth, and Shearer continued with the sport as he progressed through school. He was educated at Gosforth Central Middle School and Gosforth High School. Growing up, he played on the streets of his hometown and was originally a midfielder because "it meant [he] could get more involved in the games".[6] Shearer captained his school team and helped a Newcastle City Schools team win a seven-a-side tournament at St James' Park, before joining the amateur Wallsend Boys Club as a teenager. It was while playing for the Wallsend club that he was spotted by Southampton's scout Jack Hixon, which resulted in him spending his summers training with the club's youth team, a time he would later refer to as "the making of me".[6] Shearer had successful trials for First Division clubs West Bromwich Albion, Manchester City and Newcastle United, before being offered a youth contract with Southampton in April 1986.[6]
Club career
1986–1992: Southampton
Shearer was promoted to the first team after spending two years with the youth squad. He made his professional debut for Southampton on 26 March 1988, coming on as a substitute in a First Division fixture at Chelsea,[1] before prompting national headlines in his full debut at The Dell two weeks later. He scored a hat-trick, helping the team to a 4–2 victory against Arsenal, thus becoming the youngest player – at 17 years, 240 days – to score a hat-trick in the top division, breaking Jimmy Greaves' 30-year–old record.[1] Shearer ended the 1987–88 season with three goals in five games, and was rewarded with his first professional contract.[6]
Despite this auspicious start to his career, Shearer was only eased into the first team gradually and made just ten goalless appearances for the club the following season. Throughout his career Shearer was recognised for his strength,[7] which, during his time at Southampton, enabled him to retain the ball and provide opportunities for teammates.[1] Playing as a lone striker between wide men, Rod Wallace and Matt Le Tissier, Shearer scored three goals in 26 appearances in the 1989–90 season,[8] and in the next, four goals in 36 games. His performances in the centre of the Saints attack were soon recognised by the fans, who voted him their Player of the Year for 1991.[6][8]
In the middle of 1991, Shearer was a member of the England national under-21 football squad in the Toulon Tournament in Toulon, France. Shearer was the star of the tournament where he scored seven goals in four games.[8] It was during the 1991–92 season that Shearer rose to national prominence. 13 goals in 41 appearances for the Saints led to an England call-up;[9] he scored on his debut,[10] and was strongly linked in the press with a summer move to Manchester United. A possible move for Shearer was being mentioned in the media during late autumn of 1991, but he rejected talk of a transfer and vowed to see out the season with Southampton, resisting the temptation of a possible transfer to the two clubs who headed the title race for most of the season. Speculation of a transfer to Liverpool, who finished the season as FA Cup winners, also came to nothing.[6]
During the middle of 1992, Southampton's manager, Ian Branfoot, became "the most popular manager in English football", as he took telephone calls from clubs "trying to bargain with players they don't want plus cash". Although Branfoot accepted that a sale was inevitable, he claimed that "whatever happens, we are in the driving seat".[11] In July 1992, Shearer was sold to Blackburn Rovers for a fee of £3.6 million, with David Speedie reluctantly moving to The Dell as part of the deal. Despite Branfoot's claim to be "in the driving seat", Saints failed to include a "sell-on clause" in the contract. Shearer, less than a month off his 22nd birthday, was the most expensive player in British football.[12] In his four years in the Southampton first team, Shearer made a total of 158 appearances in all competitions, scoring 43 goals.[8]
1992–1996: Blackburn Rovers
Despite making just one goalless appearance as England failed to progress past the Euro 1992 group stages,[13] Shearer was soon subject to an English transfer record-breaking £3.6 million bid from Blackburn Rovers.[14] Although there was also interest from Manchester United manager Alex Ferguson, Blackburn benefactor Jack Walker's millions were enough to prise the striker from Southampton, and Shearer moved north to Ewood Park in the middle of 1992.[15]
On 15 August 1992, the opening weekend of the first Premier League season, Shearer scored twice against Crystal Palace with two strikes from the edge of the 18-yard box.[16] He missed half of his first season with Blackburn through injury after snapping his right anterior cruciate ligament in a match against Leeds United in December 1992, but scored 16 goals in the 21 games in which he did feature.[9] Shearer also became a regular in the England team this season and scored his second international goal; it came in a 4–0 1994 FIFA World Cup qualifier win over Turkey in November. Shearer was forced to miss January through to May due to injury and England's World Cup qualification chances were hit by a run of poor form.[6]
Returning to fitness for the 1993–94 season, he scored 31 goals from 40 games as Blackburn finished runners-up in the Premier League.[9] His performances for the club led to him being named the Football Writers' Association Footballer of the Year for that season.[17] On the international scene, England had failed to qualify for the 1994 World Cup finals,[18] but Shearer added three more goals to his international tally before embarking on his most successful domestic season as a player to date.[15]
"Shearer is the classic working class sporting hero ... everything legend demands an English centre-forward should be ... As a striker he comes closer to fitting the Roy of the Rovers fantasy than anyone else lately admired by English crowds".
Shearer as described in The Guardian on 10 April 1995.[19]
The arrival of Chris Sutton for the 1994–95 season established a strong attacking partnership at Blackburn. Shearer's 34 goals, coupled with Sutton's 15, helped the Lancashire club take the Premier League title from archrivals Manchester United on the final day of the season,[20] and the duo gained the nickname "the SAS" (Shearer And Sutton).[15] After being asked by the press how he planned to celebrate winning the title, Shearer replied with "creosoting the fence".[21] Shearer also had his first taste of European football in the UEFA Cup that season, and scored in the second leg as Blackburn went out in the first round, losing to Trelleborgs FF of Sweden.[22] His efforts for the club led to Shearer being awarded the PFA Players' Player of the Year for 1995.[23]
Although the club could not retain the title the following year, Shearer again ended the (now 38-game) season as Premier League top scorer, with 31 goals in 35 games,[24][25][26] as Blackburn finished seventh in the league. The previous season's first-place finish also saw the club enter the Champions League. Shearer's only goal in six full Champions League games was a penalty in a 4–1 victory against Rosenborg BK in the final fixture[15] and Blackburn finished third in their group, failing to progress to the next stage.[27]
He passed the 100-goal milestone for Blackburn in all competitions on 23 September 1995, scoring a hat-trick in their 5–1 home win over Coventry City in the Premier League. On 30 December, he scored his 100th Premier League goal, making him the first player to hit the landmark, in a 2–1 home win over Tottenham Hotspur. His final tally for the club was 112 goals in the Premier League and 130 in all competitions. His final goals for the club came on 17 April 1996, when he scored twice in a 3–2 home league win over Wimbledon.[28]
Shearer's international strike rate had also dried up, with no goals in the twelve matches leading up to Euro 96.[15] He missed the final three games of the season for his club due to injury, but recovered in time to play in England's UEFA European Championship campaign.[29]
1996–2006: Newcastle United
After Euro 96, Manchester United and Real Madrid again sought to sign Shearer, and attempted to enter the battle for his signature.[30] Manchester United chairman Martin Edwards and Real Madrid president Lorenzo Sanz stated that Blackburn Rovers refused to let Shearer go to Old Trafford or Estadio Santiago Bernabéu. Ultimately Shearer joined his boyhood club: Newcastle United, Manchester United's title rivals.[31]
On 30 July 1996, for a world transfer record-breaking £15 million (equivalent to £36 million today),[notes 2] Shearer joined his hometown club and league runners-up Newcastle United, managed by his hero Keegan.[6][33][34]
Shearer's 2019 validated equivalent (£222m)[32] in comparison to top transfer records in 2023
Rank	Player	From	To	Fee	Year	Ref.
1	Alan Shearer	England Blackburn	England Newcastle	£222m	1996	[32]
2	Neymar	Spain Barcelona	France Paris Saint-Germain	£198m	2017	[35][36]
3	Kylian Mbappé	France Monaco	France Paris Saint-Germain	£163m	2018	[37]
4	João Félix	Portugal Benfica	Spain Atlético Madrid	£112.9	2019	[38]
Shearer made his league debut away at Everton, on 17 August 1996,[39] and maintained his form during the rest of the season, finishing as Premier League top-scorer for the third consecutive season with 25 goals in 31 Premier League games,[26][40][41] as well as winning another PFA Player of the Year accolade,[23] despite a groin injury forcing him to miss seven matches. Among his best performances of the season came on 2 February 1997,[42] when Newcastle went into the final 15 minutes of the game 3–1 down at home to Leicester City in the league, only for Shearer to win them the game 4–3 by scoring a late hat-trick.[43] The league title still eluded the club, who finished second in the league for a second consecutive year, with Keegan resigning midway through the season.[40]
Another injury problem, this time an ankle ligament injury sustained in a pre-season match at Goodison Park, restricted Shearer to just two goals in 17 games in the 1997–98 season. His injury was reflected in the club's form, and Newcastle finished just 13th in the Premier League. To help Shearer get over the injury, club physiotherapist Paul Ferris devised unorthodox methods. At the club's training ground at Durham University, Ferris stacked six school benches and placed Shearer on top with high-jump mats either side – the striker trying to improve his balance by standing on one leg and bending over to pick up coins while having objects thrown at him, while a crowd of student onlookers watched on.[44] United (now managed by Shearer's former Blackburn manager, Kenny Dalglish) had a good run in the FA Cup; Shearer scored the winning goal in a semi-final victory over Sheffield United as the team reached the final. The team were unable to get on the scoresheet at Wembley, and lost the game 2–0 to Arsenal.[45]
Shearer after the FA Cup final defeat in 1998
An incident during a game against Leicester City in the league saw Shearer charged with misconduct by the FA,[46] with media sources claiming that video footage showed him intentionally kicking Neil Lennon in the head following a challenge.[47] The referee of the game took no action against Shearer, and he was then cleared of all charges by the FA, with Lennon giving evidence in the player's defence.[48] Former Football Association chief Graham Kelly, who brought the charges against the player, later wrote in his autobiography that Shearer had threatened to withdraw himself from the 1998 World Cup squad if the charges were upheld, which was strenuously denied by Shearer.[49]
An almost injury-free season helped Shearer improve on his previous year's tally in the 1998–99 season, the striker converting 14 goals in 30 league games and replacing Rob Lee as Newcastle captain,[50] but Newcastle finished 13th again, with Ruud Gullit having replaced Kenny Dalglish just after the season got underway.[51] He also helped Newcastle to a second consecutive FA Cup final and qualification for the following season's UEFA Cup, scoring twice in the semi-final against Tottenham Hotspur, but they once again lost 2–0, this time to treble-chasing Manchester United.
On the opening day of the 1999–2000 season, Shearer received the first red card of his career in his 100th appearance for Newcastle.[52] After dropping Shearer to the bench in a Tyne-Wear derby loss against Sunderland,[53] the unpopular Gullit resigned to be replaced by the 66-year-old Bobby Robson.[54] Despite Gullit giving Shearer the captain's armband, reports of a rift between club captain and manager were rife, Gullit's decision to drop Shearer proved deeply unpopular with fans and his departure capped a dismal start to the season.[55] The animosity between Shearer and Gullit was later confirmed by the latter, who reportedly told the striker that he was "...the most overrated player I have ever seen."[56] Robson had tried to sign Shearer for Barcelona in 1997, making a bid of £20 million which would have seen Shearer break the world's transfer fee record for the second time in 12 months. Newcastle's manager at the time, Kenny Dalglish, rejected the offer.[57]
In Robson's first match in charge, Shearer scored five goals in an 8–0 defeat of Sheffield Wednesday.[58] With Robson in charge, the team moved away from the relegation zone, finishing in mid-table and reached the FA Cup semi-finals, but a third consecutive final was beyond them as they were beaten by Chelsea. Shearer missed only one league game and notched up 23 goals.[9]
Shearer suffered an injury-hit and frustrating season in the 2000–01 season, having retired from international football after the UEFA Euro 2000 tournament to focus on club football.[59] He managed only five goals in 19 games in the league. The 2001–02 season was much better though: Shearer bagged 23 goals in 37 league games as Newcastle finished fourth — their highest standing since 1997 — meaning they would qualify for the following season's Champions League competition. One of the most memorable incidents of the season saw Roy Keane sent off after a confrontation with Shearer during Newcastle's 4–3 win over the Red Devils in September 2001.[60][61] Shearer also saw red for the second time in his career this season, after allegedly elbowing an opposition player in a match against Charlton Athletic, but this decision was later rescinded.[62]
The 2002–03 season saw Shearer and Newcastle make their return to the UEFA Champions League. Newcastle lost their first three matches in the opening group stage, but Shearer's goal against Dynamo Kyiv,[63] coupled with further wins against Juventus and Feyenoord saw the club progress to the second group stage.[64]
"I know at first hand how fierce the gladiatorial battles are between a striker and defenders. So, to maintain your performance as a top class goalscorer over a long period of time takes phenomenal dedication, self belief and enormous willpower. If you then throw in a number of serious injuries...how many? Three? And for the man to still be producing at the highest level is really an amazing feat. After a match against Juventus I met Alex Del Piero who like myself could only speak in the most glowing of terms about Shearer. He'd terrorised the Juve defenders when the clubs met in Newcastle. They found him one of the most difficult opponents they had ever faced. The coach Marcello Lippi had been purring about Shearer's performance. So much so that his strikers Alex, David (Trezeguet) and Marcelo (Salas) were ordered to take home videos and study Shearer's display."
— Gabriel Batistuta on his admiration of Shearer, February 2003.[65]
Shearer's Champions League hat-trick against Bayer Leverkusen and a brace against Inter Milan in the second group stage helped him reach a total of seven Champions League goals, along with his 17 in 35 games in the league, and a total of 25 for the season as the team again improved to finish in third place in the Premier
"""

question = "When did Alan Shearer retire?"

# Load the model and tokenizer from local directory
#model = AutoModelForQuestionAnswering.from_pretrained(r'C:\Users\RowanBarua\saved_model2')
#tokenizer = AutoTokenizer.from_pretrained(r'C:\Users\RowanBarua\saved_tokenizer2')

st.title('BERT Question Answering App')

# Input text and question
context = st.text_area("Context", "")
question = st.text_input("Question", "")
prob_tolerance = float(st.text_input("Set Minimum Answer Probability","0.00"))

if st.button("Get Answer"):
    
    question_tokens = tokenizer(question, return_tensors='pt')
    
    
    # Tokenize inputs
    inputs = tokenizer(context, return_tensors='pt')
    # Assume cls_token_id and sep_token_id are retrieved from the tokenizer
    # Get the token IDs for the special tokens
    cls_token_id = tokenizer.cls_token_id
    sep_token_id = tokenizer.sep_token_id
    cls_token = torch.tensor([[cls_token_id]], dtype=torch.long)
    sep_token = torch.tensor([[sep_token_id]], dtype=torch.long)
    
    # Concatenate to create the complete input_ids
    #input_ids_with_special_tokens = torch.cat([cls_token, question_tokens['input_ids'], sep_token, chunk, sep_token], dim=1)
    
    # Similarly, modify the attention mask
    cls_attention_mask = torch.tensor([[1]], dtype=torch.long)  # Attention mask for [CLS] token
    sep_attention_mask = torch.tensor([[1]], dtype=torch.long)  # Attention mask for [SEP] token
    
    num_tokens = inputs['input_ids'].shape[1]
    
    chunks = []
    next_token = 0
    
    while True:
        last_token = min(num_tokens-1,next_token+480)
        chunks.append(inputs['input_ids'][:,next_token:last_token+1])
        
        if last_token == num_tokens - 1:
            break
    
    
        next_token += 240
    
    for i in range(0,len(chunks)):
    # Run the model
        
        chunk = chunks[i]
        context_attention_mask = torch.ones_like(chunk)  # Attention mask for the context
        
        inputs = {
            'input_ids': torch.cat([cls_token,question_tokens['input_ids'],sep_token, chunk,sep_token], dim=1),
            'attention_mask': torch.cat([cls_attention_mask,question_tokens['attention_mask'],sep_attention_mask,context_attention_mask,sep_attention_mask], dim=1)
        }
        
    
        outputs = model(**inputs)
        
        # Sort start and end logits for multiple spans
        start_logits = outputs.start_logits
        end_logits = outputs.end_logits
        
        # Apply softmax to get the probabilities
        start_probs = softmax(start_logits, dim=-1)
        end_probs = softmax(end_logits, dim=-1)
        
        # Get the top N start and end indices with the highest probabilities
        N = 12  # Number of spans to capture
        top_start_indices = torch.topk(start_logits, N).indices.squeeze()
        top_end_indices = torch.topk(end_logits, N).indices.squeeze()
        
        min_index = -1
        max_index = -1
        
        answers = []
        for start_index, end_index in zip(top_start_indices, top_end_indices):
            if end_index >= start_index:  # Valid span
                if end_index <= min_index or max_index <= start_index:
                    
                    start_prob = start_probs[0][start_index].item()
                    end_prob = end_probs[0][end_index].item()
                   
                    # Calculate the combined probability as the product of start and end probabilities
                    answer_prob = start_prob * end_prob
                    # Calculate the combined probability as 
            
                    answer_tokens = inputs["input_ids"][0][start_index: end_index+1]
                    answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)
                    
                    if answer_prob > prob_tolerance and answer.strip():
                        answers.append((answer,answer_prob))
        
                    
                    if start_index >= min_index:
                        min_index = start_index
                    
                    if end_index >= max_index:
                        max_index = end_index
                        
        # Print all captured answers
        for idx, (answer, prob) in enumerate(answers):
            st.write(f"Answer: {answer} (Probability: {prob:.4f})")


