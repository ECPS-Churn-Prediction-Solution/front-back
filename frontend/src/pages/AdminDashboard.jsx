import React from 'react';
import styled from 'styled-components';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: '1월', 판매: 400 },
  { name: '2월', 판매: 300 },
  { name: '3월', 판매: 500 },
  { name: '4월', 판매: 200 },
  { name: '5월', 판매: 600 },
];

const AdminDashboard = () => {
  return (
    <Container>
      <h1>관리자 대시보드</h1>
      <Section>
        <h2>월별 매출</h2>
        <ChartArea>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="판매" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </ChartArea>
      </Section>
    </Container>
  );
};

export default AdminDashboard;

const Container = styled.div`
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1rem;
`;

const Section = styled.section`
  margin-top: 2rem;
`;

const ChartArea = styled.div`
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 2rem;
`;