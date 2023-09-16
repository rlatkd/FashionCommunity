from flask import Flask, render_template,request,redirect,url_for,session,flash
import sys
import database, img_resize
from os import path, remove
from werkzeug.utils import secure_filename
from urllib.parse import quote_plus


app = Flask(__name__, static_folder='./resources/')
app.secret_key = 'secretkey'
UPLOAD_FOLDER = path.join('.', 'resources/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods = ["GET", "POST"])
def index():
    #print(session['id'])
    board_data_lst = []
    board_data = database.get_main_data()
    for data in board_data:
        data_dic = {
            'id' : data[0],
            'image' : data[1],
            'create_time' : data[2],
            'content' : data[3],
            'views' : data[4],
            'title' : data[5],
            'user_id' : data[6],
            'comment_cnt' : data[7]
        }
        board_data_lst.append(data_dic)
    print(board_data_lst)
    if request.method == "POST":
        sorting_option = request.form['sorting_option']
    
        if sorting_option == "최신순":
            sorted_time_data_lst = sorted(board_data_lst, key=lambda x: x['create_time'], reverse=True)
            if 'id' in session:
                return render_template("index.html", data_lst = sorted_time_data_lst, id = session['id'])
            else:
                return render_template("index.html", data_lst = sorted_time_data_lst)
        else:
            sorted_views_data_lst = sorted(board_data_lst, key=lambda x: x['views'], reverse=True)
            if 'id' in session:
                return render_template("index.html", data_lst = sorted_views_data_lst, id = session['id'])
            else:
                return render_template("index.html", data_lst = sorted_views_data_lst)
        
    else:
        sorted_time_data_lst = sorted(board_data_lst, key=lambda x: x['create_time'], reverse=True)
        if 'id' in session:
            return render_template("index.html",data_lst=sorted_time_data_lst, id = session['id'])
        else: 
            return render_template("index.html",data_lst=sorted_time_data_lst)


@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        id_ = request.form['id']
        pwd = request.form['password']

        isid = database.id_check(id_, pwd)
        if(isid) :
            session['id'] = id_
            return redirect(url_for('index'))
        else:
            flash("로그인 정보가 없습니다. 재로그인 해주세요. ")
            return redirect(url_for('login'))

@app.route('/logout', methods = ["GET"])     
def logout():
    session.clear()
    print("here")
    return redirect(url_for('index'))
    #return id_info

@app.route('/create', methods=['POST','GET'])
def create_board_data():   
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        img_file = request.files['image']

        if img_file.filename:
            img_file.save(path.join(app.config['UPLOAD_FOLDER'], secure_filename(img_file.filename)))
            ImgFile = '/resources/' + img_file.filename
            img_resize.img_resize('.'+ ImgFile)
            database.post_board_data(session['id'],title,content,ImgFile)
        else:
            ImgFile = '/resources/no_image.png'
            img_resize.img_resize('.'+ ImgFile)
            database.post_board_data(session['id'],title,content,ImgFile)
        #database.post_board_data(sess,title,content,img_file.filename)
        return redirect(url_for('index'))
    else:
        if 'id' in session:
            return render_template('create.html')
        else:
            flash("로그인 정보가 없습니다. 재로그인 해주세요. ")
            return redirect(url_for('index'))

@app.route('/detail/<id>',methods = ["POST","GET"])
def detail(id):
    if request.method == "GET":
        database.count_view(id)
        detail_data = database.get_detail_data(id)
        detail_data_dic = {
            'id' : detail_data[0],
            'image' : detail_data[1],
            'create_time' : detail_data[2],
            'content' : detail_data[3],
            'views' : detail_data[4],
            'title' : detail_data[5],
            'user_id' : detail_data[6],
            'comment_cnt' : detail_data[7]
            }
        reply_data_lst = []
        reply_data = database.get_comments(id)
        for data in reply_data:
            reply_data_dic = {
                'user_id' : data[0],
                'content' : data[1],
                'created_time' : data[2],
                'reply_id' : data[3]
            }
            reply_data_lst.append(reply_data_dic)
        print(reply_data_lst)
        return render_template('detail.html',data=detail_data_dic, reply_data = reply_data_lst)
    else :
        if 'id' in session:
            content = request.form['content']
            user_id = session['id']
            database.comments(user_id, content, id)
            return redirect(url_for("detail", id = id))
        else:
            flash("로그인을 해야 댓글 입력이 가능합니다.")
            return redirect(url_for("detail", id = id))
@app.route('/updatereply', methods=["GET", "POST"])     
def updatereply():
    if request.method == 'POST':
        uc = request.form['updated_content']
        ri = request.form['reply_id']
        database.upate_reply(uc, ri)
    return redirect(url_for('detail', id = str(request.form['board_id'])))

@app.route('/deletereply', methods=['GET', 'POST'])
def deletereply():
    if request.method == 'POST':
        database.delete_reply(request.form['reply_id'])
    return redirect(url_for('detail', id = str(request.form['board_id'])))
@app.route('/signup', methods = ["GET", "POST"])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    else:
        id_ = request.form['id']
        pwd = request.form['password']
        name_ = request.form['name']
        phone_ = request.form['phone']
        
        isid = database.checkid_duplicate(id_)
        if(isid) :
            flash("중복된 아이디 입니다. ")
            return redirect(url_for('signup'))
        else:
            database.signup(id_, pwd, name_, phone_)
            flash("회원가입 되셨습니다. ")
            session['id'] = id_
            return redirect(url_for('index'))

# mypage
@app.route('/mypage')
def mypage():
    id = session.get('id')
    return render_template('mypage.html',id=id)



@app.route('/my_board_lst')
def my_board_lst():
    id = session.get('id')
    bd_data= database.get_my_board_lst(id)
    bd_data_lst = []
    for data in bd_data:
        bd_data_dic = {
            'title' : data[0],
            'board_id' : data[1]
        }
        bd_data_lst.append(bd_data_dic)
    return render_template('my_board_lst.html', id=id, bd_data_lst=bd_data_lst)
    
# edit
@app.route('/edit/<string:title>', methods=["POST", "GET"])
def edit(title):
    if request.method == 'POST':
        new_title = request.form['new_title']
        content = request.form['content']
        img_file = request.files['image']
        
        edit_data = database.get_edit(title)
        
        # print("123123123123123123123123")
        # print(edit_data[0][11:], img_file.filename)
        # print("123123123123123123123123")
        
        if img_file.filename:
            #print("이미지 이씀")
            remove('.' + edit_data[0])    
            img_file.save(path.join(app.config['UPLOAD_FOLDER'], secure_filename(img_file.filename)))
            ImgFile = '/resources/' + img_file.filename
            img_resize.img_resize('.'+ ImgFile)
            database.post_edit(ImgFile, title,content,new_title)
        else:
            #print("이미지 없음")
            database.post_edit(edit_data[0], title,content,new_title)
  
        return redirect(url_for('index')) 

    
    else:
        #print(title)
        #database.count_view(title)
        edit_data = database.get_edit(title)
        edit_data_dic = {

            'image' : edit_data[0],
            'content': edit_data[1],
            'title': edit_data[2]
       
            }
        return render_template('edit.html', data=edit_data_dic)



@app.route('/delete_board/<board_id>', methods = ["POST","GET"])
def delete_board(board_id):
    #title_encoded = quote_plus(title)
    if request.method == "GET":
        print("delete 화면 잘뜸")
        print(board_id)
        return render_template('delete_board.html',board_id = board_id)
    else:
        btn_action = request.form['action']
        bd_id = request.form['bd_id']
        if btn_action == "board_delete":
            database.delete_board(session['id'],int(bd_id))
            return redirect(url_for("index"))
        else:
            return redirect(url_for("index"))
        

#account change
#GET요청 : session에 저장된 user_id 정보를 불러와서 랜더링
#POST요청 : 수정된 user_id 정보를 DB에 저장 or 계정 삭제
@app.route('/acnt_chng', methods = ["POST","GET"])
def acnt_chng():
    if request.method == "GET":
        user_info = database.get_user_info(session['id'])
        print("-----------------")
        print(user_info)
        print("----------------")
        user_info_dic = {
            'id' :user_info[0],
            'pwd':user_info[3],
            'name':user_info[1],
            'phone': user_info[2]
        }
        print(user_info_dic)
        return render_template('acnt_chng.html',user_info_dic = user_info_dic)
    else:
        button_action = request.form['action']
        if button_action == "account_update":
            id = request.form['id']
            password = request.form['password']
            name = request.form['Name']
            Telephone = request.form['Telephone']
            database.update_user_info(session['id'],id, password, name, Telephone)
            session['id'] = id
        else:
            print("account_delete")
            id = request.form['id']
            database.delete_user_info(id)
            session.clear()
        return redirect(url_for('index'))
        


if __name__ == '__main__':
    app.run(debug=True)
