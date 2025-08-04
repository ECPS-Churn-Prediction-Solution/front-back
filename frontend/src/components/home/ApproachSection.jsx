import React from 'react';
import styled from 'styled-components';
import SectionTitle from '../common/SectionTitle';

const ApproachSection = () => (
  <Section>
    <SectionTitle>OUR APPROACH TO FASHION DESIGN</SectionTitle>
    <Text>
      at elegant vogue, we blend creativity with craftmanship to create fashion that transcends trends, and ensure that each of time each design is meticulously crafted, ensuring the highest quality exquisite finish
    </Text>
  </Section>
);

const Section = styled.section`
  margin: 5rem 0 4rem 0;
  text-align: center;
`;
const Text = styled.p`
  color: #444;
  font-size: 1.1rem;
  max-width: 600px;
  margin: 2rem auto 0 auto;
  line-height: 1.7;
`;

export default ApproachSection;