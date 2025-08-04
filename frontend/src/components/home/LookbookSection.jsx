import React from 'react';
import styled from 'styled-components';

const images = [
  '/mock-images/collection1.jpg',
  '/mock-images/collection2.jpg',
  '/mock-images/week1.jpg',
  '/mock-images/week2.jpg',
];

const LookbookSection = () => (
  <Section>
    <Row>
      {images.map((src, idx) => (
        <ImgBox key={idx}>
          <Img src={src} alt={`lookbook${idx+1}`} />
        </ImgBox>
      ))}
    </Row>
  </Section>
);

const Section = styled.section`
  margin: 4rem 0 3rem 0;
`;
const Row = styled.div`
  display: flex;
  gap: 2rem;
  justify-content: center;
`;
const ImgBox = styled.div`
  flex: 1 1 0;
  min-width: 180px;
  max-width: 260px;
  overflow: hidden;
  border-radius: 12px;
`;
const Img = styled.img`
  width: 100%;
  height: 220px;
  object-fit: cover;
`;

export default LookbookSection;