import React from 'react';
import styled from 'styled-components';

const Footer = () => (
  <FooterContainer>
    <FooterContent>
      <FooterSection>
        <h4>고객 지원</h4>
        <p>문의하기</p>
        <p>FAQ</p>
        <p>배송 및 반품</p>
      </FooterSection>
      <FooterSection>
        <h4>회사</h4>
        <p>회사 소개</p>
        <p>채용</p>
        <p>매장</p>
      </FooterSection>
      <FooterSection>
        <h4>팔로우하세요</h4>
        <p>Instagram</p>
        <p>Facebook</p>
        <p>Twitter</p>
      </FooterSection>
      <FooterSection>
        <h4>뉴스레터 구독</h4>
        <NewsletterForm>
          <NewsletterInput type="email" placeholder="이메일 주소" />
          <SubscribeButton>구독</SubscribeButton>
        </NewsletterForm>
      </FooterSection>
    </FooterContent>
    <FooterBottom>
      <Copyright>© 2024 YourLogo. 모든 권리 보유.</Copyright>
    </FooterBottom>
  </FooterContainer>
);

const FooterContainer = styled.footer`
  width: 100vw;
  background: #fff;
  border-top: 1px solid #e5e5e5;
  padding: 3rem 0 1.5rem 0;
  margin-top: 0;
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
`;

const FooterContent = styled.div`
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 3rem;
  max-width: 1200px;
  margin: 0 auto 2rem auto;
  width: 100%;
  flex-wrap: wrap;
  @media (max-width: 900px) {
    flex-direction: column;
    align-items: center;
    gap: 2rem;
  }
`;

const FooterSection = styled.div`
  flex: 1;
  min-width: 180px;
  max-width: 250px;
  text-align: left;
  @media (max-width: 900px) {
    text-align: center;
    max-width: 100%;
  }
  h4 {
    font-size: 1.05rem;
    font-weight: bold;
    margin-bottom: 1rem;
    color: #222;
  }
  p {
    margin-bottom: 0.5rem;
    color: #666;
    font-size: 0.97rem;
    cursor: pointer;
    &:hover {
      text-decoration: underline;
    }
  }
`;

const NewsletterForm = styled.form`
  display: flex;
  gap: 0.5rem;
  @media (max-width: 900px) {
    flex-direction: column;
    gap: 0.5rem;
    align-items: center;
  }
`;

const NewsletterInput = styled.input`
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.97rem;
`;

const SubscribeButton = styled.button`
  padding: 0.5rem 1.2rem;
  background: #222;
  color: #fff;
  border-radius: 4px;
  font-size: 0.97rem;
`;

const FooterBottom = styled.div`
  text-align: center;
  font-size: 0.93rem;
  color: #aaa;
  width: 100%;
`;

const Copyright = styled.div`
  margin-top: 1.5rem;
`;

export default Footer;
