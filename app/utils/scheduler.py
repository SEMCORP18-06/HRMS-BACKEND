from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import random
from bson.objectid import ObjectId
from pymongo import UpdateOne

from ..database import db
from .mailer import send_email

scheduler = BackgroundScheduler()

def seed_quotes_library():
    try:
        if db.quotes.count_documents({}) >= 300:
            return
            
        default_quotes = [
            {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
            {"text": "Your time is limited, so don't waste it living someone else's life.", "author": "Steve Jobs"},
            {"text": "Have the courage to follow your heart and intuition.", "author": "Steve Jobs"},
            {"text": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
            {"text": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
            {"text": "Great things in business are never done by one person. They're done by a team of people.", "author": "Steve Jobs"},
            {"text": "Details matter, it's worth waiting to get it right.", "author": "Steve Jobs"},
            {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
            {"text": "If you are going through hell, keep going.", "author": "Winston Churchill"},
            {"text": "Success is stumbling from failure to failure with no loss of enthusiasm.", "author": "Winston Churchill"},
            {"text": "We make a living by what we get, but we make a life by what we give.", "author": "Winston Churchill"},
            {"text": "Attitude is a little thing that makes a big difference.", "author": "Winston Churchill"},
            {"text": "To improve is to change; to be perfect is to change often.", "author": "Winston Churchill"},
            {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
            {"text": "Do what you can, with what you have, where you are.", "author": "Theodore Roosevelt"},
            {"text": "It is hard to fail, but it is worse never to have tried to succeed.", "author": "Theodore Roosevelt"},
            {"text": "Far and away the best prize that life has to offer is the chance to work hard at work worth doing.", "author": "Theodore Roosevelt"},
            {"text": "With self-discipline, almost anything is possible.", "author": "Theodore Roosevelt"},
            {"text": "Keep your eyes on the stars, and your feet on the ground.", "author": "Theodore Roosevelt"},
            {"text": "Act as if what you do makes a difference. It does.", "author": "William James"},
            {"text": "The greatest discovery of my generation is that a human being can alter his life by altering his attitudes.", "author": "William James"},
            {"text": "Believe that life is worth living and your belief will help create the fact.", "author": "William James"},
            {"text": "The art of being wise is the art of knowing what to overlook.", "author": "William James"},
            {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
            {"text": "No one can make you feel inferior without your consent.", "author": "Eleanor Roosevelt"},
            {"text": "Do one thing every day that scares you.", "author": "Eleanor Roosevelt"},
            {"text": "Great minds discuss ideas; average minds discuss events; small minds discuss people.", "author": "Eleanor Roosevelt"},
            {"text": "The giving of love is an education in itself.", "author": "Eleanor Roosevelt"},
            {"text": "Spread love everywhere you go. Let no one ever come to you without leaving happier.", "author": "Mother Teresa"},
            {"text": "I alone cannot change the world, but I can cast a stone across the waters to create many ripples.", "author": "Mother Teresa"},
            {"text": "Kind words can be short and easy to speak, but their echoes are truly endless.", "author": "Mother Teresa"},
            {"text": "If you judge people, you have no time to love them.", "author": "Mother Teresa"},
            {"text": "Peace begins with a smile.", "author": "Mother Teresa"},
            {"text": "If you want to live a happy life, tie it to a goal, not to people or things.", "author": "Albert Einstein"},
            {"text": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein"},
            {"text": "A person who never made a mistake never tried anything new.", "author": "Albert Einstein"},
            {"text": "Imagination is more important than knowledge.", "author": "Albert Einstein"},
            {"text": "Try not to become a man of success, but rather try to become a man of value.", "author": "Albert Einstein"},
            {"text": "Strive not to be a success, but rather to be of value.", "author": "Albert Einstein"},
            {"text": "The start is the most important part of the work.", "author": "Plato"},
            {"text": "Knowing yourself is the beginning of all wisdom.", "author": "Aristotle"},
            {"text": "Quality is not an act, it is a habit.", "author": "Aristotle"},
            {"text": "Well begun is half done.", "author": "Aristotle"},
            {"text": "Excellence is never an accident. It is always the result of high intention.", "author": "Aristotle"},
            {"text": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "author": "Aristotle"},
            {"text": "He who overcomes himself is the mightiest warrior.", "author": "Lao Tzu"},
            {"text": "The journey of a thousand miles begins with one step.", "author": "Lao Tzu"},
            {"text": "Silence is a source of great strength.", "author": "Lao Tzu"},
            {"text": "A good traveler has no fixed plans and is not intent on arriving.", "author": "Lao Tzu"},
            {"text": "Kindness in words creates confidence. Kindness in thinking creates profoundness.", "author": "Lao Tzu"},
            {"text": "It does not matter how slowly you go as long as you do not stop.", "author": "Confucius"},
            {"text": "Our greatest glory is not in never falling, but in rising every time we fall.", "author": "Confucius"},
            {"text": "Life is really simple, but we insist on making it complicated.", "author": "Confucius"},
            {"text": "Real knowledge is to know the extent of one's ignorance.", "author": "Confucius"},
            {"text": "The will to win, the desire to succeed, the urge to reach your full potential... these are the keys.", "author": "Confucius"},
            {"text": "When you reach the end of your rope, tie a knot in it and hang on.", "author": "Franklin D. Roosevelt"},
            {"text": "The only limit to our realization of tomorrow will be our doubts of today.", "author": "Franklin D. Roosevelt"},
            {"text": "Happiness lies in the joy of achievement and the thrill of creative effort.", "author": "Franklin D. Roosevelt"},
            {"text": "The greatest glory in living lies not in never falling, but in rising every time we fall.", "author": "Nelson Mandela"},
            {"text": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
            {"text": "Education is the most powerful weapon which you can use to change the world.", "author": "Nelson Mandela"},
            {"text": "For to be free is not merely to cast off one's chains, but to live in a way that respects and enhances the freedom of others.", "author": "Nelson Mandela"},
            {"text": "A winner is a dreamer who never gives up.", "author": "Nelson Mandela"},
            {"text": "Do not go where the path may lead, go instead where there is no path and leave a trail.", "author": "Ralph Waldo Emerson"},
            {"text": "The only person you are destined to become is the person you decide to be.", "author": "Ralph Waldo Emerson"},
            {"text": "To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment.", "author": "Ralph Waldo Emerson"},
            {"text": "What lies behind us and what lies before us are tiny matters compared to what lies within us.", "author": "Ralph Waldo Emerson"},
            {"text": "Adopt the pace of nature: her secret is patience.", "author": "Ralph Waldo Emerson"},
            {"text": "In the end, it's not the years in your life that count. It's the life in your years.", "author": "Abraham Lincoln"},
            {"text": "Whatever you are, be a good one.", "author": "Abraham Lincoln"},
            {"text": "Leave nothing for tomorrow which can be done today.", "author": "Abraham Lincoln"},
            {"text": "I am a slow walker, but I never walk back.", "author": "Abraham Lincoln"},
            {"text": "Whether you think you can, or you think you can't--you're right.", "author": "Henry Ford"},
            {"text": "Failure is simply the opportunity to begin again, this time more intelligently.", "author": "Henry Ford"},
            {"text": "Coming together is a beginning; keeping together is progress; working together is success.", "author": "Henry Ford"},
            {"text": "Quality means doing it right when no one is looking.", "author": "Henry Ford"},
            {"text": "You will face many defeats in life, but never let yourself be defeated.", "author": "Maya Angelou"},
            {"text": "Try to be a rainbow in someone's cloud.", "author": "Maya Angelou"},
            {"text": "We may encounter many defeats but we must not be defeated.", "author": "Maya Angelou"},
            {"text": "Nothing can dim the light which shines from within.", "author": "Maya Angelou"},
            {"text": "The best and most beautiful things in the world cannot be seen or even touched - they must be felt with the heart.", "author": "Helen Keller"},
            {"text": "Keep your face to the sunshine and you cannot see a shadow.", "author": "Helen Keller"},
            {"text": "Optimism is the faith that leads to achievement. Nothing can be done without hope and confidence.", "author": "Helen Keller"},
            {"text": "Alone we can do so little; together we can do so many.", "author": "Helen Keller"},
            {"text": "You have power over your mind - not outside events. Realize this, and you will find strength.", "author": "Marcus Aurelius"},
            {"text": "The happiness of your life depends upon the quality of your thoughts.", "author": "Marcus Aurelius"},
            {"text": "Waste no more time arguing about what a good man should be. Be one.", "author": "Marcus Aurelius"},
            {"text": "Difficulties strengthen the mind, as labor does the body.", "author": "Seneca"},
            {"text": "Luck is what happens when preparation meets opportunity.", "author": "Seneca"},
            {"text": "Associate with people who are likely to improve you.", "author": "Seneca"},
            {"text": "Nothing is impossible, the word itself says, 'I'm possible!'", "author": "Audrey Hepburn"},
            {"text": "The question isn't who is going to let me; it's who is going to stop me.", "author": "Ayn Rand"},
            {"text": "We can easily forgive a child who is afraid of the dark; the real tragedy of life is when men are afraid of the light.", "author": "Plato"},
            {"text": "Small opportunities are often the beginning of great enterprises.", "author": "Demosthenes"},
            {"text": "The mind is not a vessel to be filled, but a fire to be kindled.", "author": "Plutarch"},
            {"text": "Perseverance is the hard work you do after you get tired of doing the hard work you already did.", "author": "Newt Gingrich"},
            {"text": "Opportunities multiply as they are seized.", "author": "Sun Tzu"},
            {"text": "There is no road to path, path is made by walking.", "author": "Antonio Machado"},
            {"text": "You miss 100% of the shots you don't take.", "author": "Wayne Gretzky"},
            {"text": "Never let the fear of striking out keep you from playing the game.", "author": "Babe Ruth"},
            {"text": "Keep smiling, because life is a beautiful thing and there's so much to smile about.", "author": "Marilyn Monroe"},
            {"text": "When you have a dream, you've got to grab it and never let go.", "author": "Carol Burnett"},
            {"text": "I can't change the direction of the wind, but I can adjust my sails to always reach my destination.", "author": "Jimmy Dean"},
            {"text": "No act of kindness, no matter how small, is ever wasted.", "author": "Aesop"},
            {"text": "What you get by achieving your goals is not as important as what you become by achieving your goals.", "author": "Zig Ziglar"},
            {"text": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle Onassis"},
            {"text": "Happiness is not something ready made. It comes from your own actions.", "author": "Dalai Lama"},
            {"text": "Empower your team, embrace change, and foster a culture of continuous learning.", "author": "Satya Nadella"},
            {"text": "Always stay grounded and remember where you came from.", "author": "Sundar Pichai"},
            {"text": "When something is important enough, you do it even if the odds are not in your favor.", "author": "Elon Musk"},
            {"text": "Work hard, have fun, make history.", "author": "Jeff Bezos"},
            {"text": "Patience is a key element of success.", "author": "Bill Gates"},
            {"text": "Risk comes from not knowing what you're doing.", "author": "Warren Buffett"},
            {"text": "Leadership is about making others better as a result of your presence.", "author": "Sheryl Sandberg"},
            {"text": "Great leaders inspire people to believe in themselves.", "author": "Indra Nooyi"},
            {"text": "Let your joy be in your journey, not in some distant goal.", "author": "Tim Cook"},
            {"text": "Believe in what you are doing, take responsibility, and don't make excuses.", "author": "Howard Schultz"},
            {"text": "Business opportunities are like buses, there's always another one coming.", "author": "Richard Branson"},
            {"text": "The way to get started is to quit talking and begin doing.", "author": "Walt Disney"},
            {"text": "Be the change that you wish to see in the world.", "author": "Mahatma Gandhi"},
            {"text": "You cannot cross the sea merely by standing and staring at the water.", "author": "Rabindranath Tagore"},
            {"text": "You have to dream before your dreams can come true.", "author": "A.P.J. Abdul Kalam"},
            {"text": "Arise, awake, and stop not till the goal is reached.", "author": "Swami Vivekananda"},
            {"text": "Clear thinking requires courage rather than intelligence.", "author": "Thomas Edison"},
            {"text": "Energy and persistence conquer all things.", "author": "Benjamin Franklin"},
            {"text": "Honesty is the first chapter in the book of wisdom.", "author": "Thomas Jefferson"},
            {"text": "It is not height, but depth that makes a mountain majestic.", "author": "C.S. Lewis"},
            {"text": "All we have to decide is what to do with the time that is given us.", "author": "J.R.R. Tolkien"},
            {"text": "The secret of getting ahead is getting started.", "author": "Mark Twain"},
            {"text": "Be yourself; everyone else is already taken.", "author": "Oscar Wilde"},
            {"text": "Even the darkest night will end and the sun will rise.", "author": "Victor Hugo"},
            {"text": "If you want to be happy, be.", "author": "Leo Tolstoy"},
            {"text": "He who has a why to live can bear almost any how.", "author": "Friedrich Nietzsche"},
            {"text": "I am not what happened to me, I am what I choose to become.", "author": "Carl Jung"},
            {"text": "Knowing is not enough; we must apply. Willing is not enough; we must do.", "author": "Johann Wolfgang von Goethe"},
            {"text": "Talent wins games, but teamwork and intelligence win championships.", "author": "Michael Jordan"},
            {"text": "Great things come from hard work and perseverance. No excuses.", "author": "Kobe Bryant"},
            {"text": "I really think a champion is defined not by their wins but by how they can recover when they fall.", "author": "Serena Williams"},
            {"text": "Don't count the days, make the days count.", "author": "Muhammad Ali"},
            {"text": "Perfection is not attainable, but if we chase perfection we can catch excellence.", "author": "Vince Lombardi"},
            {"text": "Success is peace of mind, which is a direct result of self-satisfaction in knowing you made the effort to become the best of which you are capable.", "author": "John Wooden"},
            {"text": "The best way to predict the future is to create it.", "author": "Peter Drucker"},
            {"text": "People don't buy what you do; they buy why you do it.", "author": "Simon Sinek"},
            {"text": "Don't find customers for your products, find products for your customers.", "author": "Seth Godin"},
            {"text": "Either you run the day or the day runs you.", "author": "Jim Rohn"},
            {"text": "The key is not to prioritize what's on your schedule, but to schedule your priorities.", "author": "Stephen Covey"},
            {"text": "You do not rise to the level of your goals. You fall to the level of your systems.", "author": "James Clear"},
            {"text": "Courage is not the absence of fear, but the triumph over it.", "author": "Nelson Mandela"},
            {"text": "Vulnerability is not winning or losing; it's having the courage to show up when you can't control the outcome.", "author": "Brené Brown"},
            {"text": "Focus on being productive instead of busy.", "author": "Tim Ferriss"},
            {"text": "Simplicity is the ultimate sophistication.", "author": "Leonardo da Vinci"},
            {"text": "What gets measured gets managed.", "author": "Peter Drucker"},
            {"text": "Your culture is your brand.", "author": "Tony Hsieh"},
            {"text": "Culture eats strategy for breakfast.", "author": "Peter Drucker"},
            {"text": "In diversity there is beauty and there is strength.", "author": "Maya Angelou"},
            {"text": "Small daily improvements over time lead to stunning results.", "author": "Robin Sharma"},
            {"text": "Don't wait. The time will never be just right.", "author": "Napoleon Hill"},
            {"text": "Everything you've ever wanted is on the other side of fear.", "author": "George Addair"},
            {"text": "Dream big and dare to fail.", "author": "Norman Vaughan"},
            {"text": "Action is the foundational key to all success.", "author": "Pablo Picasso"},
            {"text": "Do what is right, not what is easy nor what is popular.", "author": "Roy T. Bennett"},
            {"text": "Hard work beats talent when talent fails to work hard.", "author": "Tim Notke"},
            {"text": "Discipline is choosing between what you want now and what you want most.", "author": "Abraham Lincoln"},
            {"text": "Focus on the solution, not the problem.", "author": "Jim Rohn"},
            {"text": "Doubt kills more dreams than failure ever will.", "author": "Suzy Kassem"},
            {"text": "Be so good they can't ignore you.", "author": "Steve Martin"},
            {"text": "Integrity is doing the right thing, even when no one is watching.", "author": "C.S. Lewis"},
            {"text": "Turn your wounds into wisdom.", "author": "Oprah Winfrey"},
            {"text": "The secret of change is to focus all of your energy not on fighting the old, but on building the new.", "author": "Socrates"},
            {"text": "Light tomorrow with today.", "author": "Elizabeth Barrett Browning"},
            {"text": "Never bend your head. Always hold it high. Look the world straight in the eye.", "author": "Helen Keller"},
            {"text": "Start where you are. Use what you have. Do what you can.", "author": "Arthur Ashe"},
            {"text": "Build your own dreams, or someone else will hire you to build theirs.", "author": "Farrah Gray"},
            {"text": "The harder I work, the luckier I get.", "author": "Samuel Goldwyn"},
            {"text": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
            {"text": "Success consists of getting up just one more time than you fall.", "author": "Oliver Goldsmith"},
            {"text": "Everything has beauty, but not everyone sees it.", "author": "Confucius"},
            {"text": "Choose a job you love, and you will never have to work a day in your life.", "author": "Confucius"},
            {"text": "A goal is a dream with a deadline.", "author": "Napoleon Hill"},
            {"text": "It is never too late to be what you might have been.", "author": "George Eliot"},
            {"text": "Whatever the mind of man can conceive and believe, it can achieve.", "author": "Napoleon Hill"},
            {"text": "Work hard in silence, let your success be your noise.", "author": "Frank Ocean"},
            {"text": "Failure is the condiment that gives success its flavor.", "author": "Truman Capote"},
            {"text": "If you want to go fast, go alone. If you want to go far, go together.", "author": "African Proverb"},
            {"text": "Leadership is the capacity to translate vision into reality.", "author": "Warren Bennis"},
            {"text": "The challenge of leadership is to be strong, but not rude; be kind, but not weak.", "author": "Jim Rohn"},
            {"text": "To lead people, walk behind them.", "author": "Lao Tzu"},
            {"text": "A leader is one who knows the way, goes the way, and shows the way.", "author": "John C. Maxwell"},
            {"text": "Management is about arranging and telling. Leadership is about nurturing and enhancing.", "author": "Tom Peters"},
            {"text": "Continuous improvement is better than delayed perfection.", "author": "Mark Twain"},
            {"text": "Focus on quality, and quantity will follow.", "author": "Steve Jobs"},
            {"text": "When you change the way you look at things, the things you look at change.", "author": "Wayne Dyer"},
            {"text": "There are no shortcuts to any place worth going.", "author": "Beverly Sills"},
            {"text": "If opportunity doesn't knock, build a door.", "author": "Milton Berle"},
            {"text": "You can't use up creativity. The more you use, the more you have.", "author": "Maya Angelou"},
            {"text": "Do what you love, and love what you do.", "author": "Ray Bradbury"},
            {"text": "Stay true to yourself, yet always be open to learning.", "author": "Deepak Chopra"},
            {"text": "Learn from yesterday, live for today, hope for tomorrow.", "author": "Albert Einstein"},
            {"text": "What we achieve inwardly will change outer reality.", "author": "Plutarch"},
            {"text": "Strive for perfection, settled for excellence.", "author": "J.C. Penney"},
            {"text": "The function of leadership is to produce more leaders, not more followers.", "author": "Ralph Nader"},
            {"text": "A genuine leader is not a searcher for consensus but a molder of consensus.", "author": "Martin Luther King Jr."},
            {"text": "Faith is taking the first step even when you don't see the whole staircase.", "author": "Martin Luther King Jr."},
            {"text": "Darkness cannot drive out darkness; only light can do that.", "author": "Martin Luther King Jr."},
            {"text": "The time is always right to do what is right.", "author": "Martin Luther King Jr."},
            {"text": "Injustice anywhere is a threat to justice everywhere.", "author": "Martin Luther King Jr."},
            {"text": "We must accept finite disappointment, but never lose infinite hope.", "author": "Martin Luther King Jr."},
            {"text": "Live as if you were to die tomorrow. Learn as if you were to live forever.", "author": "Mahatma Gandhi"},
            {"text": "Strength does not come from physical capacity. It comes from an indomitable will.", "author": "Mahatma Gandhi"},
            {"text": "An ounce of practice is worth more than tons of preaching.", "author": "Mahatma Gandhi"},
            {"text": "The best way to find yourself is to lose yourself in the service of others.", "author": "Mahatma Gandhi"},
            {"text": "Where there is love there is life.", "author": "Mahatma Gandhi"},
            {"text": "Change your thoughts and you change your world.", "author": "Norman Vincent Peale"},
            {"text": "Shoot for the moon. Even if you miss, you'll land among the stars.", "author": "Norman Vincent Peale"},
            {"text": "Believe in yourself and all that you are.", "author": "Christian D. Larson"},
            {"text": "Your passion is waiting for your courage to catch up.", "author": "Isabelle Lafleche"},
            {"text": "Work like there is someone working twenty-four hours a day to take it away from you.", "author": "Mark Cuban"},
            {"text": "If you don't build your dream, someone else will hire you to help them build theirs.", "author": "Dhirubhai Ambani"},
            {"text": "Think big, think fast, think ahead. Ideas are no one's monopoly.", "author": "Dhirubhai Ambani"},
            {"text": "Challenge the status quo and push the boundaries of what is possible.", "author": "Ratan Tata"},
            {"text": "None can destroy iron, but its own rust can. Likely, none can destroy a person, but their own mindset can.", "author": "Ratan Tata"},
            {"text": "I don't believe in taking right decisions. I take decisions and then make them right.", "author": "Ratan Tata"},
            {"text": "If you want to walk fast, walk alone. But if you want to walk far, walk together.", "author": "Ratan Tata"},
            {"text": "Take the stones people throw at you and use them to build a monument.", "author": "Ratan Tata"},
            {"text": "Empowering employees means giving them the freedom to innovate and excel.", "author": "N.R. Narayana Murthy"},
            {"text": "Respect, recognition, and reward are the pillars of a great workplace.", "author": "N.R. Narayana Murthy"},
            {"text": "Our assets walk out of the door each evening. We have to make sure that they return the next morning.", "author": "N.R. Narayana Murthy"},
            {"text": "Character is how you treat those who can do nothing for you.", "author": "Johann Wolfgang von Goethe"},
            {"text": "Kindness is a language which the deaf can hear and the blind can see.", "author": "Mark Twain"},
            {"text": "The two most important days in your life are the day you are born and the day you find out why.", "author": "Mark Twain"},
            {"text": "Keep away from people who try to belittle your ambitions.", "author": "Mark Twain"},
            {"text": "Continuous effort - not strength or intelligence - is the key to unlocking our potential.", "author": "Winston Churchill"},
            {"text": "Courage is grace under pressure.", "author": "Ernest Hemingway"},
            {"text": "There is nothing noble in being superior to your fellow man; true nobility is being superior to your former self.", "author": "Ernest Hemingway"},
            {"text": "The world breaks everyone and afterward many are strong at the broken places.", "author": "Ernest Hemingway"},
            {"text": "Today is a new day. You're off to Great Places! You're off and away!", "author": "Dr. Seuss"},
            {"text": "You have brains in your head. You have feet in your shoes. You can steer yourself any direction you choose.", "author": "Dr. Seuss"},
            {"text": "Why fit in when you were born to stand out?", "author": "Dr. Seuss"},
            {"text": "Sometimes the questions are complicated and the answers are simple.", "author": "Dr. Seuss"},
            {"text": "Unless someone like you cares a whole awful lot, nothing is going to get better. It's not.", "author": "Dr. Seuss"}
        ]
        
        ops = [UpdateOne({"text": q["text"]}, {"$setOnInsert": q}, upsert=True) for q in default_quotes]
        db.quotes.bulk_write(ops)
    except Exception as e:
        print(f"[SCHEDULER] Error seeding quote library: {str(e)}")

# Generate exactly spaced business days and assign quotes for the given month
def ensure_daily_pulse_schedule(year, month):
    try:
        tenant_id = "semco"
        
        TARGET_PULSES_PER_MONTH = 12

        # Ensure quote library is seeded
        seed_quotes_library()

        quotes = list(db.quotes.find({}))

        # Get all business days in this month
        import calendar
        num_days = calendar.monthrange(year, month)[1]
        business_days = []
        for d in range(1, num_days + 1):
            date_obj = datetime(year, month, d)
            if date_obj.weekday() < 5:  # Monday to Friday
                business_days.append(date_obj.date().isoformat())

        if not business_days:
            return

        # Find existing scheduled dates for this month
        existing_schedules = list(db.daily_pulse_schedule.find({
            "tenant_id": tenant_id,
            "date": {"$regex": f"^{year}-{month:02d}-"}
        }))
        existing_dates = {s["date"] for s in existing_schedules}

        # Available unassigned business days
        available_days = [bd for bd in business_days if bd not in existing_dates]
        needed_slots = min(TARGET_PULSES_PER_MONTH - len(existing_dates), len(available_days))

        if needed_slots <= 0:
            return

        # Pick needed_slots random business days
        selected_dates = random.sample(available_days, needed_slots)
        selected_dates.sort()

        # Avoid quote reuse: find all quote texts scheduled or delivered so far
        used_quote_texts = {s["quote"] for s in db.daily_pulse_schedule.find({"tenant_id": tenant_id}, {"quote": 1})}

        # Filter available quotes to get unused ones
        unused_quotes = [q for q in quotes if q.get("text") not in used_quote_texts]

        # Fallback to all quotes if we ran out of unused ones
        if len(unused_quotes) < needed_slots:
            unused_quotes = quotes

        selected_quotes = random.sample(unused_quotes, needed_slots) if len(unused_quotes) >= needed_slots else (unused_quotes * needed_slots)[:needed_slots]

        for i, target_date in enumerate(selected_dates):
            db.daily_pulse_schedule.insert_one({
                "tenant_id": tenant_id,
                "date": target_date,
                "time": "10:30",
                "quote": selected_quotes[i].get("text"),
                "author": selected_quotes[i].get("author", "Unknown"),
                "status": "Scheduled",
                "delivered_at": None
            })
        print(f"[SCHEDULER] Generated {needed_slots} Daily Pulses for {year}-{month:02d}. Total scheduled: {len(existing_dates) + needed_slots}.")
    except Exception as e:
        print(f"[SCHEDULER] Error generating Daily Pulse schedule: {str(e)}")

# Daily Pulse Quote Sender (9:00 AM Blast to active employee corporate emails)
def check_and_send_daily_pulse():
    try:
        tenant_id = "semco"
        now_dt = datetime.now()
        today = now_dt.date().isoformat()
        print(f"[SCHEDULER] Running Daily Pulse check for today ({today})...")
        
        # Check if already delivered today
        already_delivered = db.daily_pulse_schedule.find_one({
            "tenant_id": tenant_id,
            "date": today,
            "status": "Delivered"
        })
        if already_delivered:
            print(f"[SCHEDULER] Daily Pulse for today ({today}) was already delivered. Skipping duplicate dispatch.")
            return

        # Find scheduled pulse for today
        pulse = db.daily_pulse_schedule.find_one({
            "tenant_id": tenant_id,
            "date": today,
            "status": "Scheduled"
        })
        
        # If no pulse pre-scheduled for today, create one automatically if today is a business day (Mon-Fri)
        if not pulse:
            if now_dt.weekday() < 5:  # Monday to Friday
                print(f"[SCHEDULER] No pre-scheduled pulse for today ({today}). Auto-selecting quote from library...")
                quotes = list(db.quotes.find({}))
                if not quotes:
                    print(f"[SCHEDULER] No quotes in library for auto-dispatch on {today}.")
                    return
                
                # Pick unused quote
                used_texts = {s["quote"] for s in db.daily_pulse_schedule.find({"tenant_id": tenant_id}, {"quote": 1})}
                unused = [q for q in quotes if q.get("text") not in used_texts]
                selected_q = random.choice(unused) if unused else random.choice(quotes)
                
                pulse_id = db.daily_pulse_schedule.insert_one({
                    "tenant_id": tenant_id,
                    "date": today,
                    "time": "10:30",
                    "quote": selected_q.get("text"),
                    "author": selected_q.get("author", "Unknown"),
                    "status": "Scheduled",
                    "delivered_at": None
                }).inserted_id
                
                pulse = db.daily_pulse_schedule.find_one({"_id": pulse_id})
            else:
                print(f"[SCHEDULER] Today ({today}) is a weekend. Skipping automatic Daily Pulse blast.")
                return

        # Delta-sync: get all active corporate emails (Company Email Address)
        employees = list(db.employees.find({
            "tenant_id": pulse.get("tenant_id", "semco"),
            "status": "ACTIVE"
        }))
        
        emails = [emp.get("email") for emp in employees if emp.get("email")]
        if not emails:
            print(f"[SCHEDULER] No active employee emails for Daily Pulse blast on {today}")
            return
            
        quote_text = pulse.get("quote")
        quote_author = pulse.get("author", "Unknown")
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 20px; color: #1e293b;">
                <div style="background-color: white; padding: 30px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                    <h2 style="color: #3b82f6; border-bottom: 2px solid #eff6ff; padding-bottom: 10px; margin-top: 0;">Daily Pulse 🌟</h2>
                    <blockquote style="font-size: 18px; font-style: italic; color: #334155; border-left: 4px solid #3b82f6; padding-left: 15px; margin: 20px 0;">
                        "{quote_text}"
                    </blockquote>
                    <p style="text-align: right; font-weight: bold; color: #64748b;">— {quote_author}</p>
                    <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                    <p style="font-size: 12px; color: #94a3b8; text-align: center;">You received this as part of your company's daily motivation program.</p>
                </div>
            </body>
        </html>
        """
        
        to_emails_str = ", ".join(emails)
        send_email(to_emails_str, "Daily Pulse 🌟", body)
        
        # Mark as delivered
        db.daily_pulse_schedule.update_one(
            {"_id": pulse["_id"]},
            {
                "$set": {
                    "status": "Delivered",
                    "delivered_at": datetime.now().isoformat()
                }
            }
        )
        print(f"[SCHEDULER] Successfully dispatched Daily Pulse blast to {len(emails)} recipients on {today}.")
    except Exception as e:
        print(f"[SCHEDULER] Daily Pulse dispatch error: {str(e)}")

# Event Reminders Sender
def send_event_reminder(event_id_str: str, interval_name: str):
    try:
        event = db.events.find_one({"_id": ObjectId(event_id_str)})
        if not event:
            print(f"[SCHEDULER] Event {event_id_str} not found for reminder {interval_name}")
            return
            
        title = event["title"]
        description = event.get("description", "")
        start_time_str = event["start_time"]
        location = event.get("location", "")
        attendees = event.get("attendees", [])
        
        # If no specific attendees were selected, default to all active employees as fallback
        if not attendees:
            employees = list(db.employees.find({"tenant_id": event.get("tenant_id", "semco"), "status": "ACTIVE"}))
            attendees = [{
                "name": emp.get("name"),
                "email": emp.get("email"),
                "personal_email": emp.get("personal_email")
            } for emp in employees]
        
        for att in attendees:
            emails_to_send = []
            if att.get("email"):
                emails_to_send.append(att["email"])
            if att.get("personal_email"):
                emails_to_send.append(att["personal_email"])
                
            to_email_str = ", ".join([e for e in emails_to_send if e])
            if not to_email_str:
                continue
                
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 20px; color: #1e293b;">
                    <div style="background-color: white; padding: 30px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                        <h2 style="color: #ec4899; border-bottom: 2px solid #fdf2f8; padding-bottom: 10px; margin-top: 0;">Upcoming Event Reminder 📅</h2>
                        <h3 style="color: #0f172a; margin-bottom: 5px;">{title}</h3>
                        <p style="font-size: 14px; color: #64748b; margin-top: 0;"><b>When:</b> {start_time_str}</p>
                        <p style="font-size: 14px; color: #64748b; margin-top: 0;"><b>Location:</b> {location or 'N/A'}</p>
                        <div style="background-color: #fafafa; border-radius: 6px; padding: 15px; margin-top: 15px; border-left: 4px solid #ec4899;">
                            <p style="margin: 0; font-size: 14px;">{description or 'No description provided.'}</p>
                        </div>
                        <p style="font-size: 13px; color: #94a3b8; margin-top: 20px;">This is a {interval_name} reminder for the event.</p>
                    </div>
                </body>
            </html>
            """
            send_email(to_email_str, f"Reminder: {title} ({interval_name})", body)
    except Exception as e:
        print(f"[SCHEDULER] Event reminder error: {str(e)}")

def send_immediate_event_invitation(event_id_str: str):
    try:
        event = db.events.find_one({"_id": ObjectId(event_id_str)})
        if not event:
            print(f"[SCHEDULER] Event {event_id_str} not found for immediate invitation")
            return
            
        title = event["title"]
        description = event.get("description", "")
        start_time_str = event["start_time"]
        location = event.get("location", "")
        attendees = event.get("attendees", [])
        
        if not attendees:
            print(f"[SCHEDULER] No specific attendees selected for immediate invitation of Event {event_id_str}")
            return
            
        # Parse start time for clean display
        try:
            dt = datetime.fromisoformat(start_time_str.replace('Z', ''))
            formatted_time = dt.strftime('%B %d, %Y at %I:%M %p')
        except Exception:
            formatted_time = start_time_str
            
        for att in attendees:
            emails_to_send = []
            if att.get("email"):
                emails_to_send.append(att["email"])
            if att.get("personal_email"):
                emails_to_send.append(att["personal_email"])
                
            to_email_str = ", ".join([e for e in emails_to_send if e])
            if not to_email_str:
                continue
                
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 20px; color: #1e293b;">
                    <div style="background-color: white; padding: 30px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                        <h2 style="color: #6366f1; border-bottom: 2px solid #eff6ff; padding-bottom: 10px; margin-top: 0;">New Event Scheduled 📅</h2>
                        <p style="font-size: 16px; line-height: 1.6; color: #334155;">
                            Hello <strong>{att.get('name', 'Team Member')}</strong>,
                        </p>
                        <p style="font-size: 16px; line-height: 1.6; color: #334155;">
                            You have been invited to a new corporate event scheduled by HR:
                        </p>
                        <h3 style="color: #0f172a; margin-bottom: 5px;">{title}</h3>
                        <p style="font-size: 14px; color: #64748b; margin-top: 0;"><b>When:</b> {formatted_time}</p>
                        <p style="font-size: 14px; color: #64748b; margin-top: 0;"><b>Location:</b> {location or 'N/A'}</p>
                        <div style="background-color: #fafafa; border-radius: 6px; padding: 15px; margin-top: 15px; border-left: 4px solid #6366f1;">
                            <p style="margin: 0; font-size: 14px;">{description or 'No description provided.'}</p>
                        </div>
                        <p style="font-size: 13px; color: #94a3b8; margin-top: 20px;">You will receive automated reminders leading up to this event.</p>
                    </div>
                </body>
            </html>
            """
            send_email(to_email_str, f"Invitation: {title}", body)
            print(f"[SCHEDULER] Sent immediate invitation for '{title}' to {att.get('name')} ({to_email_str})")
    except Exception as e:
        print(f"[SCHEDULER] Immediate invitation error: {str(e)}")

def queue_event_reminders(event_id_str, title, start_time_dt):
    """
    Queues reminders for an event at: T-30 days, T-7 days, T-1 day, and T-30 minutes.
    """
    intervals = [
        ("30 Days Before", timedelta(days=30)),
        ("7 Days Before", timedelta(days=7)),
        ("1 Day Before", timedelta(days=1)),
        ("30 Minutes Before", timedelta(minutes=30))
    ]
    
    now = datetime.now()
    
    for name, delta in intervals:
        trigger_time = start_time_dt - delta
        if trigger_time > now:
            job_id = f"event_{event_id_str}_{name.replace(' ', '_').lower()}"
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
            scheduler.add_job(
                send_event_reminder,
                'date',
                run_date=trigger_time,
                args=[event_id_str, name],
                id=job_id
            )
            print(f"[SCHEDULER] Queued reminder '{name}' for Event {event_id_str} ({title}) at {trigger_time}")
            
    # Always dispatch an immediate invitation email to confirm scheduling!
    send_immediate_event_invitation(event_id_str)

def seed_holidays_for_year(year: int):
    try:
        # Check if already seeded for this year
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        if db.holidays.count_documents({"date": {"$gte": start_date, "$lte": end_date}}) > 0:
            return
            
        # Fixed holidays in Maharashtra / Kalnirnay Calendar
        holidays = [
            {"name": "Republic Day", "date": f"{year}-01-26", "type": "National"},
            {"name": "Chhatrapati Shivaji Maharaj Jayanti", "date": f"{year}-02-19", "type": "Bank"},
            {"name": "Dr. Babasaheb Ambedkar Jayanti", "date": f"{year}-04-14", "type": "National"},
            {"name": "Maharashtra Day", "date": f"{year}-05-01", "type": "National"},
            {"name": "Independence Day", "date": f"{year}-08-15", "type": "National"},
            {"name": "Gandhi Jayanti", "date": f"{year}-10-02", "type": "National"},
            {"name": "Christmas Day", "date": f"{year}-12-25", "type": "National"},
        ]
        
        # Variable holidays mapping
        if year == 2025:
            holidays.extend([
                {"name": "New Year's Day", "date": "2025-01-01", "type": "Bank"},
                {"name": "Maha Shivratri", "date": "2025-02-26", "type": "Bank"},
                {"name": "Holi (Dhulivandan)", "date": "2025-03-14", "type": "Bank"},
                {"name": "Gudi Padwa", "date": "2025-03-30", "type": "Bank"},
                {"name": "Ramzan Eid (Id-ul-Fitr)", "date": "2025-03-31", "type": "Bank"},
                {"name": "Good Friday", "date": "2025-04-18", "type": "Bank"},
                {"name": "Bakri Eid", "date": "2025-06-07", "type": "Bank"},
                {"name": "Ganesh Chaturthi", "date": "2025-08-27", "type": "Bank"},
                {"name": "Dussehra", "date": "2025-10-02", "type": "Bank"},
                {"name": "Diwali (Lakshmi Pujan)", "date": "2025-10-20", "type": "Bank"},
            ])
        elif year == 2026:
            holidays.extend([
                {"name": "New Year's Day", "date": "2026-01-01", "type": "Bank"},
                {"name": "Maha Shivratri", "date": "2026-02-15", "type": "Bank"},
                {"name": "Holi (Dhulivandan)", "date": "2026-03-03", "type": "Bank"},
                {"name": "Gudi Padwa", "date": "2026-03-19", "type": "Bank"},
                {"name": "Ramzan Eid (Id-ul-Fitr)", "date": "2026-03-21", "type": "Bank"},
                {"name": "Ram Navami", "date": "2026-03-26", "type": "Bank"},
                {"name": "Good Friday", "date": "2026-04-03", "type": "Bank"},
                {"name": "Bakri Eid", "date": "2026-05-28", "type": "Bank"},
                {"name": "Moharram", "date": "2026-06-26", "type": "Bank"},
                {"name": "Id-E-Milad", "date": "2026-08-26", "type": "Bank"},
                {"name": "Ganesh Chaturthi", "date": "2026-09-14", "type": "Bank"},
                {"name": "Dussehra", "date": "2026-10-20", "type": "Bank"},
                {"name": "Diwali (Lakshmi Pujan)", "date": "2026-11-08", "type": "Bank"},
            ])
        elif year == 2027:
            holidays.extend([
                {"name": "New Year's Day", "date": "2027-01-01", "type": "Bank"},
                {"name": "Maha Shivratri", "date": "2027-03-06", "type": "Bank"},
                {"name": "Ramzan Eid (Id-ul-Fitr)", "date": "2027-03-10", "type": "Bank"},
                {"name": "Holi (Dhulivandan)", "date": "2027-03-22", "type": "Bank"},
                {"name": "Good Friday", "date": "2027-03-26", "type": "Bank"},
                {"name": "Gudi Padwa", "date": "2027-04-07", "type": "Bank"},
                {"name": "Bakri Eid", "date": "2027-05-17", "type": "Bank"},
                {"name": "Ganesh Chaturthi", "date": "2027-09-04", "type": "Bank"},
                {"name": "Dussehra", "date": "2027-10-09", "type": "Bank"},
                {"name": "Diwali (Lakshmi Pujan)", "date": "2027-10-29", "type": "Bank"},
            ])
        else:
            # Astronomical astrological prediction algorithm for variable festivals.
            # Using Metonic shift offsets and astronomical/astrological lunar approximations.
            # 1. Maha Shivratri (usually late Feb or early Mar, moves back ~11 days unless leap month correction)
            # Baseline: 2026-02-15.
            diff_years = year - 2026
            shift_days = (diff_years * 11) % 30
            m_day = 15 - shift_days
            m_month = 2
            if m_day <= 0:
                m_day = 28 + m_day
                m_month = 2
            elif m_day < 5:
                # Leap month adjustment shift
                m_day = m_day + 15
                
            # 2. Holi (Dhulivandan) - Baseline: 2026-03-03
            holi_shift = (diff_years * 11) % 30
            h_day = 3 - holi_shift
            h_month = 3
            if h_day <= 0:
                h_day = 28 + h_day
                h_month = 2
            if h_day < 5:
                h_day = h_day + 19
                
            # 3. Gudi Padwa (Chaitra Shukla Pratipada) - Baseline: 2026-03-19
            padwa_shift = (diff_years * 11) % 30
            p_day = 19 - padwa_shift
            p_month = 3
            if p_day <= 0:
                p_day = 30 + p_day
                p_month = 3
            if p_day < 10:
                p_day = p_day + 19
                
            # 4. Ramzan Eid (Id-ul-Fitr) - Baseline: 2026-03-21
            # Islamic calendar shifts ~11 days backward every year consistently
            eid_total_shift = diff_years * 11
            # Base date: Day of year for Mar 21 is 80 (non-leap estimation)
            base_doy = 80
            eid_doy = base_doy - eid_total_shift
            if eid_doy <= 0:
                # Cycle forward into previous year or wraps
                eid_doy = 365 + eid_doy
            eid_dt = datetime(year, 1, 1) + timedelta(days=eid_doy - 1)
            eid_str = eid_dt.date().isoformat()
            
            # 5. Ganesh Chaturthi (Bhadrapada Shukla Chaturthi) - Baseline: 2026-09-14
            gc_shift = (diff_years * 11) % 30
            gc_day = 14 - gc_shift
            gc_month = 9
            if gc_day <= 0:
                gc_day = 31 + gc_day
                gc_month = 8
            if gc_day < 5:
                gc_day = gc_day + 19
                
            # 6. Dussehra (Vijayadashami) - Baseline: 2026-10-20
            dus_shift = (diff_years * 11) % 30
            d_day = 20 - dus_shift
            d_month = 10
            if d_day <= 0:
                d_day = 30 + d_day
                d_month = 9
            if d_day < 5:
                d_day = d_day + 19
                
            # 7. Diwali (Lakshmi Pujan - Amavasya) - Baseline: 2026-11-08
            diw_shift = (diff_years * 11) % 30
            dw_day = 8 - diw_shift
            dw_month = 11
            if dw_day <= 0:
                dw_day = 31 + dw_day
                dw_month = 10
            if dw_day < 5:
                dw_day = dw_day + 19

            holidays.extend([
                {"name": "New Year's Day", "date": f"{year}-01-01", "type": "Bank"},
                {"name": "Maha Shivratri (Predicted)", "date": f"{year}-{m_month:02d}-{m_day:02d}", "type": "Bank"},
                {"name": "Holi (Dhulivandan) (Predicted)", "date": f"{year}-{h_month:02d}-{h_day:02d}", "type": "Bank"},
                {"name": "Gudi Padwa (Predicted)", "date": f"{year}-{p_month:02d}-{p_day:02d}", "type": "Bank"},
                {"name": "Ramzan Eid (Id-ul-Fitr) (Predicted)", "date": eid_str, "type": "Bank"},
                {"name": "Good Friday", "date": f"{year}-04-03", "type": "Bank"}, # placeholder
                {"name": "Ganesh Chaturthi (Predicted)", "date": f"{year}-{gc_month:02d}-{gc_day:02d}", "type": "Bank"},
                {"name": "Dussehra (Predicted)", "date": f"{year}-{d_month:02d}-{d_day:02d}", "type": "Bank"},
                {"name": "Diwali (Lakshmi Pujan) (Predicted)", "date": f"{year}-{dw_month:02d}-{dw_day:02d}", "type": "Bank"},
            ])
            
        db.holidays.insert_many(holidays)
        print(f"[SCHEDULER] Seeded {len(holidays)} Maharashtra public holidays for the year {year}.")
    except Exception as e:
        print(f"[SCHEDULER] Error seeding holidays for year {year}: {str(e)}")

def seed_holidays():
    try:
        # Clear database holidays to avoid duplicates and refresh with updated list
        db.holidays.delete_many({})
        
        # Seed holidays for past year, current year, and next year
        today = datetime.now()
        seed_holidays_for_year(today.year - 1)
        seed_holidays_for_year(today.year)
        seed_holidays_for_year(today.year + 1)
    except Exception as e:
        print(f"[SCHEDULER] Holiday seeding error: {str(e)}")

def check_and_send_holiday_notifications():
    try:
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        tomorrow_str = tomorrow.isoformat()
        
        holiday = db.holidays.find_one({"date": tomorrow_str})
        if holiday:
            h_name = holiday["name"]
            h_type = holiday.get("type", "National")
            print(f"[SCHEDULER] Tomorrow is a {h_type} Holiday: {h_name}. Dispatching notifications to all active employees...")
            
            employees = list(db.employees.find({"status": "ACTIVE"}))
            for emp in employees:
                emails_to_send = []
                if emp.get("email"):
                    emails_to_send.append(emp["email"])
                if emp.get("personal_email"):
                    emails_to_send.append(emp["personal_email"])
                    
                to_email_str = ", ".join([e for e in emails_to_send if e])
                if not to_email_str:
                    continue
                    
                body = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; background-color: #f0fdf4; padding: 20px; color: #1e293b;">
                        <div style="background-color: white; padding: 30px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                            <h2 style="color: #16a34a; border-bottom: 2px solid #f0fdf4; padding-bottom: 10px; margin-top: 0;">Holiday Notice: Tomorrow is {h_name} 🏖️</h2>
                            <p style="font-size: 16px; line-height: 1.6; color: #334155;">
                                Hello <strong>{emp.get('name', 'Team Member')}</strong>,
                            </p>
                            <p style="font-size: 16px; line-height: 1.6; color: #334155;">
                                Please note that tomorrow, <strong>{tomorrow.strftime('%B %d, %Y')}</strong>, is an official <strong>{h_type} Holiday</strong> in celebration of <strong>{h_name}</strong>.
                            </p>
                            <div style="background-color: #f0fdf4; border-radius: 8px; padding: 15px; margin: 20px 0; border-left: 4px solid #16a34a; text-align: center; font-size: 18px; font-weight: bold; color: #15803d;">
                                🎉 Have a restful and wonderful holiday! 🎉
                            </div>
                            <p style="font-size: 14px; color: #94a3b8; text-align: center; margin-top: 20px;">This is an automated holiday notification sent to your company and personal email addresses.</p>
                        </div>
                    </body>
                </html>
                """
                send_email(to_email_str, f"Holiday Notice: Tomorrow is {h_name} 🏖️", body)
                print(f"[SCHEDULER] Holiday notice successfully sent to {emp.get('name')} ({to_email_str})")
    except Exception as e:
        print(f"[SCHEDULER] Holiday notifications check error: {str(e)}")

def try_parse_date(date_str):
    if not date_str:
        return None
    date_str = str(date_str).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str[:10], fmt).date()
        except ValueError:
            continue
    return None

def get_ordinal_suffix(number):
    if 11 <= (number % 100) <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
    return f"{number}{suffix}"

def check_and_send_celebrations():
    try:
        today = datetime.now().date()
        print(f"[SCHEDULER] Running daily check for Birthdays and Work Anniversaries today ({today})...")
        employees = list(db.employees.find({"status": "ACTIVE"}))
        for emp in employees:
            dept = emp.get("department") or "General"
            desg = emp.get("designation") or emp.get("role") or "Employee"

            # ── Birthday ───────────────────────────────────────────────────────
            dob_val = emp.get("dob") or emp.get("birthday")
            if dob_val:
                b_date = try_parse_date(dob_val)
                if b_date and b_date.month == today.month and b_date.day == today.day:
                    # 1. Personal wish to the celebrant
                    subject = f"Happy Birthday, {emp.get('name', 'Employee')}! 🎂🎉"
                    body = f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; background-color: #fdf2f8; padding: 20px; color: #1e293b;">
                            <div style="background-color: white; padding: 40px 30px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center;">
                                <h2 style="color: #ec4899; text-align: center; margin-bottom: 8px;">Happy Birthday, {emp.get('name', 'Employee')}! 🎂🎈</h2>
                                <p style="font-size: 16px; line-height: 1.6; color: #475569; text-align: center; margin: 0 auto 20px; max-width: 480px;">
                                    On behalf of the entire team, we wish you a fantastic birthday filled with joy, laughter, and success. Thank you for your amazing contributions to our organization!
                                </p>
                                <div style="text-align: center; font-size: 50px; margin: 24px 0;">🎉🎂🎁✨</div>
                                <p style="font-size: 14px; text-align: center; color: #94a3b8; margin-top: 24px;">Warmest wishes,<br>The People Operations Team</p>
                            </div>
                        </body>
                    </html>
                    """
                    emails_to_send = [emp.get("email")]
                    if emp.get("personal_email"):
                        emails_to_send.append(emp.get("personal_email"))
                    to_email_str = ", ".join([e for e in emails_to_send if e])
                    if to_email_str:
                        send_email(to_email_str, subject, body)
                        print(f"[SCHEDULER] Automatically sent Birthday email to {emp.get('name')} ({to_email_str})")

                    # 2. Broadcast announcement to all other active employees
                    broadcast_subject = f"Let's Celebrate {emp.get('name', 'Employee')}'s Birthday! 🥳"
                    broadcast_body = f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; background-color: #fdf2f8; padding: 20px; color: #1e293b;">
                            <div style="background-color: white; padding: 40px 30px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center;">
                                <h2 style="color: #ec4899; text-align: center; margin-bottom: 8px;">Let's Celebrate {emp.get('name', 'Employee')}'s Birthday! 🥳</h2>
                                <p style="font-size: 16px; line-height: 1.6; color: #475569; text-align: center; margin: 0 auto 20px; max-width: 480px;">
                                    Today is a special day! Please join us in wishing a very Happy Birthday to our colleague, <strong>{emp.get('name', 'Employee')}</strong>.
                                </p>
                                <p style="font-size: 15px; color: #475569; text-align: center; margin: 6px 0;"><strong>Department:</strong> {dept}</p>
                                <p style="font-size: 15px; color: #475569; text-align: center; margin: 6px 0;"><strong>Designation:</strong> {desg}</p>
                                <div style="text-align: center; font-size: 50px; margin: 24px 0;">🎉🎂🎁✨</div>
                                <p style="font-size: 14px; text-align: center; color: #94a3b8; margin-top: 24px;">Warmest wishes,<br>The People Operations Team</p>
                            </div>
                        </body>
                    </html>
                    """
                    other_emails = []
                    for other in employees:
                        if str(other["_id"]) != str(emp["_id"]):
                            if other.get("email"):
                                other_emails.append(other["email"])
                            if other.get("personal_email"):
                                other_emails.append(other["personal_email"])
                    if other_emails:
                        send_email(", ".join(other_emails), broadcast_subject, broadcast_body)
                        print(f"[SCHEDULER] Dispatched Birthday announcement for {emp.get('name')} to all other employees.")

            # ── Work Anniversary ───────────────────────────────────────────────
            doj_val = emp.get("doj") or emp.get("joining_date") or emp.get("anniversary")
            if doj_val:
                a_date = try_parse_date(doj_val)
                if a_date and a_date.month == today.month and a_date.day == today.day:
                    joining_year = a_date.year
                    years = today.year - joining_year
                    if years > 0:
                        ordinal = get_ordinal_suffix(years)

                        # 1. Personal wish to the celebrant
                        subject = f"Happy {ordinal} Work Anniversary, {emp.get('name', 'Employee')}! 🌟💼"
                        body = f"""
                        <html>
                            <body style="font-family: Arial, sans-serif; background-color: #ecfdf5; padding: 20px; color: #1e293b;">
                                <div style="background-color: white; padding: 40px 30px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center;">
                                    <h2 style="color: #10b981; text-align: center; margin-bottom: 8px;">Happy {ordinal} Work Anniversary! 🌟</h2>
                                    <p style="font-size: 18px; font-weight: bold; color: #065f46; text-align: center; margin: 0 0 16px;">🎊 Congratulations! 🎊</p>
                                    <p style="font-size: 16px; line-height: 1.6; color: #475569; text-align: center; margin: 0 auto 20px; max-width: 480px;">
                                        <b>{emp.get('name', 'Employee')}</b>, on completing your <b>{ordinal}</b> year with us! Thank you for your dedication, hard work, and support. We are proud to have you on our team.
                                    </p>
                                    <div style="text-align: center; font-size: 50px; margin: 24px 0;">💼✨🚀🏆</div>
                                    <p style="font-size: 14px; text-align: center; color: #94a3b8; margin-top: 24px;">Best regards,<br>The People Operations Team</p>
                                </div>
                            </body>
                        </html>
                        """
                        emails_to_send = [emp.get("email")]
                        if emp.get("personal_email"):
                            emails_to_send.append(emp.get("personal_email"))
                        to_email_str = ", ".join([e for e in emails_to_send if e])
                        if to_email_str:
                            send_email(to_email_str, subject, body)
                            print(f"[SCHEDULER] Automatically sent Work Anniversary email to {emp.get('name')} ({to_email_str})")

                        # 2. Broadcast announcement to all other active employees
                        broadcast_subject = f"Celebrating {emp.get('name', 'Employee')}'s {ordinal} Work Anniversary! 🚀"
                        broadcast_body = f"""
                        <html>
                            <body style="font-family: Arial, sans-serif; background-color: #ecfdf5; padding: 20px; color: #1e293b;">
                                <div style="background-color: white; padding: 40px 30px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center;">
                                    <h2 style="color: #10b981; text-align: center; margin-bottom: 8px;">Celebrating {emp.get('name', 'Employee')}'s {ordinal} Work Anniversary! 🚀</h2>
                                    <p style="font-size: 18px; font-weight: bold; color: #065f46; text-align: center; margin: 0 0 16px;">🎊 Congratulations! 🎊</p>
                                    <p style="font-size: 16px; line-height: 1.6; color: #475569; text-align: center; margin: 0 auto 20px; max-width: 480px;">
                                        Please join us in congratulating <strong>{emp.get('name', 'Employee')}</strong> on completing their <strong>{ordinal}</strong> year with SEMCO Groups!
                                    </p>
                                    <p style="font-size: 15px; color: #475569; text-align: center; margin: 6px 0;"><strong>Department:</strong> {dept}</p>
                                    <p style="font-size: 15px; color: #475569; text-align: center; margin: 6px 0;"><strong>Designation:</strong> {desg}</p>
                                    <div style="text-align: center; font-size: 50px; margin: 24px 0;">💼✨🚀🏆</div>
                                    <p style="font-size: 14px; text-align: center; color: #94a3b8; margin-top: 24px;">Best regards,<br>The People Operations Team</p>
                                </div>
                            </body>
                        </html>
                        """
                        other_emails = []
                        for other in employees:
                            if str(other["_id"]) != str(emp["_id"]):
                                if other.get("email"):
                                    other_emails.append(other["email"])
                                if other.get("personal_email"):
                                    other_emails.append(other["personal_email"])
                        if other_emails:
                            send_email(", ".join(other_emails), broadcast_subject, broadcast_body)
                            print(f"[SCHEDULER] Dispatched Work Anniversary announcement for {emp.get('name')} ({ordinal}) to all other employees.")
    except Exception as e:
        print(f"[SCHEDULER] Celebrations check error: {str(e)}")

def seed_next_months_pulses():
    """Seeds pulses for a full 12-month rolling window ahead."""
    try:
        today = datetime.now()
        for i in range(12):
            m = (today.month - 1 + i) % 12 + 1
            y = today.year + (today.month - 1 + i) // 12
            ensure_daily_pulse_schedule(y, m)
        print(f"[SCHEDULER] Monthly pulse seeder: seeded 12-month rolling window starting {today.year}-{today.month:02d}.")
    except Exception as e:
        print(f"[SCHEDULER] Monthly pulse seeder error: {str(e)}")

def init_scheduler():
    import os
    is_vercel = os.getenv("VERCEL") == "1" or "VERCEL" in os.environ
    
    # Always seed database defaults on startup
    seed_holidays()
    try:
        today = datetime.now()
        for i in range(12):
            m = (today.month - 1 + i) % 12 + 1
            y = today.year + (today.month - 1 + i) // 12
            ensure_daily_pulse_schedule(y, m)
    except Exception as e:
        print(f"[SCHEDULER] Error seeding database defaults on startup: {str(e)}")

    if is_vercel:
        print("[SCHEDULER] Running in serverless/Vercel environment. Skipping background thread scheduler initialization.")
        return

    if not scheduler.running:
        scheduler.start()
        
        scheduler.add_job(
            check_and_send_daily_pulse,
            CronTrigger(hour=10, minute=30),
            id="daily_pulse_quote_blast"
        )
        scheduler.add_job(
            check_and_send_celebrations,
            CronTrigger(hour=10, minute=30),
            id="daily_celebrations"
        )
        scheduler.add_job(
            check_and_send_holiday_notifications,
            CronTrigger(hour=9, minute=0),
            id="daily_holiday_notifications"
        )
        # Rolling monthly seeder: runs on the 1st of every month at 9:05 AM
        scheduler.add_job(
            seed_next_months_pulses,
            CronTrigger(day=1, hour=9, minute=5),
            id="monthly_pulse_seeder"
        )
        print("[SCHEDULER] Scheduler initialized and started.")
