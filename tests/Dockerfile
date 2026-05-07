FROM cypress/included:15.14.2

RUN apt-get update && apt-get install -y wait-for-it

WORKDIR /e2e
COPY package.json package-lock.json* ./
RUN npm install

COPY . .

RUN cypress verify
