import React from 'react';
import styled from 'styled-components';
import SectionTitle from '../common/SectionTitle';
import MinimalButton from '../common/MinimalButton';
import ProductCard from '../common/ProductCard';

const NewThisWeekSection = ({ data }) => (
  <Section>
    <SectionTitle right={<SeeAllBtn>See All</SeeAllBtn>}>
      {data.title} <Count>({data.count})</Count>
    </SectionTitle>
    <Row>
      {data.items.map(item => (
        <ProductCard key={item.id} image={item.imageUrl} name={item.name} price={item.price} />
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
`;
const Count = styled.span`
  color: #1a4cff;
  font-size: 1.1rem;
  margin-left: 0.5rem;
`;
const SeeAllBtn = styled(MinimalButton)`
  font-size: 0.95rem;
  padding: 0.3rem 1.2rem;
`;

export default NewThisWeekSection;