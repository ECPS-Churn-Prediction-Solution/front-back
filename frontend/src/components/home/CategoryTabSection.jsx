import React, { useState } from 'react';
import styled from 'styled-components';
import SectionTitle from '../common/SectionTitle';
import ProductCard from '../common/ProductCard';

const categories = [
  { key: 'all', label: 'All' },
  { key: 'men', label: 'Men' },
  { key: 'women', label: 'Women' },
  { key: 'kid', label: 'Kid' },
];

const sampleItems = [
  { id: 1, name: 'Basic Ivory Height T-shirt', imageUrl: '/mock-images/collection1.jpg', price: '119,000' },
  { id: 2, name: 'Soft mesh straight Aurora', imageUrl: '/mock-images/collection2.jpg', price: '139,000' },
  { id: 3, name: 'Basic Ivory Height T-shirt', imageUrl: '/mock-images/collection1.jpg', price: '119,000' },
];

const CategoryTabSection = () => {
  const [selected, setSelected] = useState('all');
  // 실제로는 카테고리별로 필터링된 상품을 보여줘야 함
  return (
    <Section>
      <SectionTitle right={<FilterSort>Sort | Filter</FilterSort>}>
        XIV COLLECTIONS 23-24
      </SectionTitle>
      <TabBar>
        {categories.map(cat => (
          <Tab key={cat.key} $active={selected === cat.key} onClick={() => setSelected(cat.key)}>
            {cat.label}
          </Tab>
        ))}
      </TabBar>
      <Row>
        {sampleItems.map(item => (
          <ProductCard key={item.id} image={item.imageUrl} name={item.name} price={item.price} />
        ))}
      </Row>
      <MoreBtn>More</MoreBtn>
    </Section>
  );
};

const Section = styled.section`
  margin: 4rem 0 3rem 0;
`;
const FilterSort = styled.div`
  color: #888;
  font-size: 1rem;
`;
const TabBar = styled.div`
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
`;
const Tab = styled.button.withConfig({
  shouldForwardProp: (prop) => prop !== '$active'
})`
  background: none;
  border: none;
  font-size: 1.1rem;
  font-weight: bold;
  color: ${({ $active }) => ($active ? '#222' : '#aaa')};
  border-bottom: 2px solid ${({ $active }) => ($active ? '#222' : 'transparent')};
  padding: 0.3rem 0.7rem;
  cursor: pointer;
  transition: color 0.2s, border 0.2s;
`;
const Row = styled.div`
  display: flex;
  gap: 2.5rem;
  margin-bottom: 2rem;
`;
const MoreBtn = styled.button`
  border: none;
  background: none;
  color: #222;
  font-size: 1rem;
  text-decoration: underline;
  cursor: pointer;
`;

export default CategoryTabSection;