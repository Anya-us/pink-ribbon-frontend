
const tokens = {
  admin: {
    token: 'admin-token'
  },
  editor: {
    token: 'editor-token'
  }
}

const users = {
  'admin-token': {
    roles: ['admin'],
    introduction: '糖网筛查演示工作空间',
    avatar: '/retina-mark.svg',
    name: '演示医护'
  },
  'editor-token': {
    roles: ['editor'],
    introduction: '糖网筛查演示工作空间',
    avatar: '/retina-mark.svg',
    name: '演示采集员'
  }
}

module.exports = [
  // user login
  {
    url: '/vue-element-admin/user/login',
    type: 'post',
    response: config => {
      const { username, password } = config.body
      const token = tokens[username]

      // mock error
      if (!token || password !== '111111') {
        return {
          code: 60204,
          message: '演示用户名为 admin 或 editor，密码为 111111。'
        }
      }

      return {
        code: 20000,
        data: token
      }
    }
  },

  // get user info
  {
    url: '/vue-element-admin/user/info\.*',
    type: 'get',
    response: config => {
      const { token } = config.query
      const info = users[token]

      // mock error
      if (!info) {
        return {
          code: 50008,
          message: 'Login failed, unable to get user details.'
        }
      }

      return {
        code: 20000,
        data: info
      }
    }
  },

  // user logout
  {
    url: '/vue-element-admin/user/logout',
    type: 'post',
    response: _ => {
      return {
        code: 20000,
        data: 'success'
      }
    }
  }
]
