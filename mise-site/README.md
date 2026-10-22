# mise 공개 웹사이트

이 폴더는 정적 웹사이트와 Vercel Python Function으로 구성되어 있습니다. 앱 주소는 브라우저 즐겨찾기에 추가하거나 HTTPS 환경에서 홈 화면에 설치할 수 있습니다. 로그인 전에는 레시피가 브라우저에 저장되고, Supabase를 연결한 뒤에는 이메일 계정에 동기화됩니다.

## Vercel 배포

1. 이 `mise-site` 폴더의 파일을 GitHub 저장소에 올립니다.
2. Vercel에서 **Add New → Project**를 선택하고 저장소를 연결합니다.
3. 프로젝트 설정에서 Root Directory를 `mise-site`로 지정하고 Deploy를 누릅니다.
4. 배포된 HTTPS 주소를 브라우저에서 열어 즐겨찾기에 추가합니다. 휴대전화에서는 브라우저 메뉴의 **홈 화면에 추가**를 선택할 수 있습니다.

별도의 빌드 명령이나 환경 변수는 필요하지 않습니다. `/api/extract` 함수는 공개 페이지의 Recipe JSON-LD 정보를 읽습니다. 사이트 로그인이나 자동 수집 차단이 있으면 수동 입력 안내를 보여줍니다.

## 계정 동기화 연결

1. Supabase에서 프로젝트를 하나 만듭니다.
2. 프로젝트의 SQL Editor에서 `supabase-setup.sql` 전체를 실행합니다. 테이블은 RLS 정책으로 각 계정이 자기 데이터만 읽고 쓸 수 있게 설정됩니다.
3. Project Settings → API Keys에서 Project URL과 publishable key를 복사합니다. 현재 프로젝트 값은 `supabase-config.js`에 반영해두었습니다. `service_role` 또는 secret key는 절대로 브라우저 파일에 넣지 마세요.
4. Authentication → URL Configuration의 Site URL과 Redirect URLs에 `https://mise-recipes-mise-site.vercel.app`을 등록한 뒤 사이트를 다시 배포합니다.
5. 사이트에서 계정을 만들고 로그인하면 현재 브라우저의 레시피를 계정에 저장합니다. 같은 계정으로 다른 기기에서 로그인하면 계정의 레시피를 불러옵니다.

로그인 전에는 레시피가 브라우저 로컬 저장 공간에 남습니다. 기존 계정으로 새 브라우저에서 처음 로그인할 때, 현재 기기의 레시피를 계정 목록에 합칠지 선택할 수 있습니다. 이메일 확인 기능이 켜져 있으면 가입 후 이메일 인증을 마친 다음 로그인해야 합니다.
